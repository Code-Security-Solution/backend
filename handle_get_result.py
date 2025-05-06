import os
import json
from flask import jsonify, request
from database import get_file_by_id
# token_required 주석 처리
# from handle_auth import token_required

# 설정 파일 로드
with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

RESULT_DIR = 'results'

# token_required 데코레이터 제거
def get_scan_result(file_id):
    """
    GET 요청: 특정 file_id의 번역된 분석 결과 JSON 반환
    /scan-result/<file_id>
    """
    # 먼저 DB에서 조회 시도
    record = get_file_by_id(file_id)
    translated_result_file = None

    if record:
        # DB에 기록이 있는 경우 (로그인한 사용자)
        translated_result_file = record.get('translated_result_file')
    else:
        # DB에 기록이 없는 경우 (비로그인 사용자)
        # 파일 시스템에서 직접 찾기
        temp_file_path = os.path.join(RESULT_DIR, f"{file_id}.json")
        if os.path.exists(temp_file_path):
            translated_result_file = temp_file_path

    # 파일을 찾지 못한 경우
    if not translated_result_file:
        return jsonify({
            'status': 404,
            'message': '해당 file_id에 대한 결과가 없습니다.',
            'result':None
        }), 404

    # 파일이 존재하는지 확인
    if not os.path.exists(translated_result_file):
        return jsonify({
            'status': 404,
            'message': '분석 결과 파일이 존재하지 않습니다.',
            'result':None
        }), 404

    try:
        with open(translated_result_file, 'r', encoding='utf-8-sig') as f:
            scan_results = json.load(f)
        return jsonify({
            'status': 200,
            'message': '성공',
            'result': scan_results
        }), 200
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': '파일 읽기 실패: ' + str(e),
            'result':None
        }), 500
