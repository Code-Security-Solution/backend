import os
import json
import uuid
import subprocess
from flask import request, jsonify
from database import insert_scan_record
from handle_auth import token_required

# 설정 파일 로드
with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

CLI_EXECUTABLE = config.get('CLI_EXECUTABLE')
UPLOAD_DIR = 'uploads'
RESULT_DIR = 'results'

# 디렉터리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

@token_required
def scan_code(current_user):
    """
    POST 요청: 파일을 받아 분석을 수행하고 결과 파일을 생성
    /scan
    """
    if 'source_code' not in request.files:
        return jsonify({
            'status': 400,
            'message': '소스코드 파일이 업로드되지 않았습니다.',
            'result':{
                }
        }), 400

    files = request.files.getlist('source_code')  # 여러 개의 파일 받기

    if not files or all(f.filename == '' for f in files):
        return jsonify({
            'status': 400,
            'message': '유효한 소스코드 파일이 없습니다.',
            'result':{
                }
        }), 400

    # 로그인 사용자의 이메일 사용
    user_email = current_user['email']

    # 고유 폴더 생성 (각 요청마다 별도 폴더)
    file_id = str(uuid.uuid4())
    upload_folder = os.path.join(UPLOAD_DIR, file_id)
    os.makedirs(upload_folder, exist_ok=True)

    file_paths = []

    # 여러 개의 파일 저장
    for file in files:
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        file_paths.append(file_path)

    result_file = os.path.join(RESULT_DIR, f"{file_id}.json")
    translated_result_file = os.path.join(RESULT_DIR, f"{file_id}_translated.json")

    # 해당 폴더에서만 스캔 실행
    command = [CLI_EXECUTABLE, 'scan', 'semgrep', upload_folder, result_file]
    # print(f"실행할 명령어: {' '.join(command)}")  # 명령어 확인 로그 - 디버그용

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')

        # print("CLI 실행 완료") - 디버그용
        # print("STDOUT:", result.stdout)  # 표준 출력 로그 확인 - 디버그용
        # print("STDERR:", result.stderr)  # 표준 에러 로그 확인 - 디버그용
    except subprocess.CalledProcessError as e:
        print(f"CLI 실행 오류 발생: {e.stderr}")  # CLI 오류 로그 확인
        return jsonify({
            'status': 500,
            'message': '분석 엔진 실행 중 오류 발생.',
            'result':{
                }
        }), 500

    # DB에 정보 저장
    insert_scan_record(user_email, file_id, file_paths, result_file, translated_result_file)

    # # 생성된 폴더 삭제하려면 추가
    # import shutil
    # shutil.rmtree(upload_folder, ignore_errors=True)

    return jsonify({
            'status': 200,
            'message': '파일이 성공적으로 분석되었습니다.',
            'result':{
                'file_id': file_id,
                'uploaded_files': file_paths
                }
        })
