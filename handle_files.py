from flask import jsonify, send_file
import os
import zipfile
import tempfile
from database import get_user_files, get_file_by_id, json_serialize
from handle_auth import token_required
from bson import ObjectId
import json

@token_required
def my_files_handler(current_user):
    # 이 함수는 사용자별 파일 목록이므로 인증 유지
    user_email = current_user['email']
    files = get_user_files(user_email)

    # MongoDB 데이터를 JSON 직렬화 가능한 형태로 변환
    serializable_files = []
    all_file_names = []  # 모든 파일 이름을 저장할 리스트

    for file in files:
        serializable_file = {}
        for key, value in file.items():
            # _id 필드는 제외
            if key == '_id':
                continue
            if isinstance(value, ObjectId):
                serializable_file[key] = str(value)
            elif isinstance(value, list):
                # 리스트 내부의 ObjectId도 변환
                serializable_file[key] = [str(item) if isinstance(item, ObjectId) else item for item in value]
            else:
                serializable_file[key] = value

        # 파일 경로에서 이름 추출
        file_paths = serializable_file.get('file_paths', [])
        uploaded_file_id = ""
        for path in file_paths:
            if os.path.exists(path):
                file_name = os.path.basename(path)
                uploaded_file_id += file_name
                all_file_names.append(file_name)

        # 파일 이름 정보 추가
        serializable_file['uploaded_file_id'] = uploaded_file_id

        file_id = serializable_file.get('file_id')
        serializable_file['download_links'] = {
            'source_single': f'/download-source/{file_id}',
            'source_all': f'/download-all-sources/{file_id}',
            'result': f'/download-result/{file_id}',
            'translated_result': f'/download-translated-result/{file_id}',
            'view_summary': f'/summary-report/{file_id}',
            'view_result': f'/scan-result/{file_id}',
            'view_detail': f'/detail-report/{file_id}'
        }
        serializable_files.append(serializable_file)

    return jsonify({
        'status': 200,
        'message': '파일 목록 조회 성공',
        'result': {
            'user_email': user_email,
            'files_count': len(serializable_files),
            'files': serializable_files,
            'files_list': all_file_names
        }
    }), 200

@token_required
def download_source_handler(current_user, file_id):
    user_email = current_user['email']
    file_info = get_file_by_id(file_id, user_email)

    if not file_info:
        return jsonify({
            'status': 404,
            'message': '파일을 찾을 수 없거나 접근 권한이 없습니다.',
            'result': {}
        }), 404

    # 파일 경로 리스트에서 첫 번째 파일만 다운로드 (여러 파일인 경우 수정 필요)
    file_path = file_info.get('file_paths', [])[0]
    if not os.path.exists(file_path):
        return jsonify({
            'status': 404,
            'message': '파일이 서버에 존재하지 않습니다.',
            'result': {}
        }), 404

    # 파일 이름 추출
    file_name = os.path.basename(file_path)

    return send_file(file_path,
                   as_attachment=True,
                   download_name=file_name,
                   mimetype='application/octet-stream')

@token_required
def download_result_handler(current_user, file_id):
    user_email = current_user['email']
    file_info = get_file_by_id(file_id, user_email)

    if not file_info:
        return jsonify({
            'status': 404,
            'message': '파일을 찾을 수 없거나 접근 권한이 없습니다.',
            'result': {}
        }), 404

    # 분석 결과 파일 경로
    result_file = file_info.get('result_file')
    if not os.path.exists(result_file):
        return jsonify({
            'status': 404,
            'message': '분석 결과 파일이 서버에 존재하지 않습니다.',
            'result': {}
        }), 404

    # 파일 이름 추출
    file_name = os.path.basename(result_file)

    return send_file(result_file,
                   as_attachment=True,
                   download_name=file_name,
                   mimetype='application/json')

@token_required
def download_translated_result_handler(current_user, file_id):
    user_email = current_user['email']
    file_info = get_file_by_id(file_id, user_email)

    if not file_info:
        return jsonify({
            'status': 404,
            'message': '파일을 찾을 수 없거나 접근 권한이 없습니다.',
            'result': {}
        }), 404

    # 번역된 분석 결과 파일 경로
    translated_result_file = file_info.get('translated_result_file')
    if not os.path.exists(translated_result_file):
        return jsonify({
            'status': 404,
            'message': '번역된 분석 결과 파일이 서버에 존재하지 않습니다.',
            'result': {}
        }), 404

    # 파일 이름 추출
    file_name = os.path.basename(translated_result_file)

    return send_file(translated_result_file,
                   as_attachment=True,
                   download_name=file_name,
                   mimetype='application/json')

@token_required
def download_all_sources_handler(current_user, file_id):
    user_email = current_user['email']
    file_info = get_file_by_id(file_id, user_email)

    if not file_info:
        return jsonify({
            'status': 404,
            'message': '파일을 찾을 수 없거나 접근 권한이 없습니다.',
            'result': {}
        }), 404

    # 모든 파일 경로 가져오기
    file_paths = file_info.get('file_paths', [])
    if not file_paths:
        return jsonify({
            'status': 404,
            'message': '다운로드할 소스 파일이, 없습니다.',
            'result': {}
        }), 404

    # 임시 zip 파일 생성
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_file.close()

    try:
        # 파일들을 zip으로 압축
        with zipfile.ZipFile(temp_file.name, 'w') as zipf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    # 원본 파일 이름만 추출하여 압축 파일에 추가
                    file_name = os.path.basename(file_path)
                    zipf.write(file_path, arcname=file_name)

        return send_file(temp_file.name,
                       as_attachment=True,
                       download_name=f'source_files_{file_id}.zip',
                       mimetype='application/zip')
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'파일 압축 중 오류가 발생했습니다: {str(e)}',
            'result': {}
        }), 500
    finally:
        # 사용 후 임시 파일 삭제 예약
        os.unlink(temp_file.name)
