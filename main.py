from flask import Flask, request, jsonify, send_file
import os
import subprocess
import json

app = Flask(__name__)

with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

# CLI 실행 파일의 경로
CLI_EXECUTABLE = config.get('CLI_EXECUTABLE')

UPLOAD_DIR = 'uploads'
RESULT_DIR = 'results'

# 디렉터리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# 분석 결과 파일 경로
RESULT_FILE = os.path.join(RESULT_DIR, 'code-scan-result.json')
TRANSLATED_RESULT_FILE = os.path.join(RESULT_DIR, 'code-scan-result_translated.json')

@app.route('/scan', methods=['POST'])
def scan_code():
    """POST 요청: 파일을 받아 분석을 수행하고 결과 파일을 생성만 함"""
    # 1. 파일 업로드 받기
    if 'source_code' not in request.files:
        return jsonify({'error': '소스코드 파일이 업로드되지 않았습니다.'}), 400
    file = request.files['source_code']
    if file.filename == '':
        return jsonify({'error': '유효한 파일명이 없습니다.'}), 400

    # 파일 저장
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(file_path)
    
    # 2. CLI 분석 엔진 호출
    # Code_Nova_Guardian.exe 실행 명령어 구성
    # 예: .\Code_Nova_Guardian.exe scan semgrep "<file_path>" "<output_file>"
    command = [
        CLI_EXECUTABLE,
        'scan',
        'semgrep',
        UPLOAD_DIR,
        RESULT_FILE
    ]
    
    try:
        # CLI 실행 (subprocess.run은 동기적으로 실행되며, 완료될 때까지 기다림)
        process = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({
            'error': '분석 엔진 실행 중 오류가 발생했습니다.',
            'details': e.stderr
        }), 500
    
    # # 4. JSON 데이터에서 원하는 정보만 추출하거나 메시지 번역 등 추가 가공
    # # 예시: results 리스트 내의 각 항목에서 file_path, line, message만 추출
    # filtered_results = []
    # for item in scan_results.get('results', []):
    #     filtered_item = {
    #         'file_path': item.get('file_path'),
    #         'line': item.get('line'),
    #         'message': item.get('message')  # 추가 번역 기능이 필요하다면 이 부분에서 번역 API 호출 가능
    #     }
    #     filtered_results.append(filtered_item)
    
    # 최종 결과를 JSON으로 반환
    return jsonify({'message': '파일이 성공적으로 분석되었습니다.', 'result_file' : RESULT_FILE})

@app.route('/scan-result', methods=['GET'])
def get_scan_result():
    """GET 요청: 최근 생성된 번역된 분석 결과 JSON 파일을 반환"""
    if not os.path.exists(TRANSLATED_RESULT_FILE):
        return jsonify({'error': '번역된 분석 결과 파일이 존재하지 않습니다.'}), 404

    try:
        with open(TRANSLATED_RESULT_FILE, 'r', encoding='utf-8-sig') as f:
            scan_results = json.load(f)
        return jsonify({'scan_results': scan_results})
    except Exception as e:
        return jsonify({
            'error': '분석 결과 파일을 읽어오는 데 실패했습니다.',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
