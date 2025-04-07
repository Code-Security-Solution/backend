import os
import json
from flask import jsonify
from database import get_scan_result_by_id
from handle_auth import token_required

@token_required
def get_scan_result(current_user, file_id):
    """
    GET 요청: 특정 file_id의 번역된 분석 결과 JSON 반환
    /scan-result/<file_id>
    """
    # 현재 사용자의 이메일로 파일 소유권 확인
    record = get_scan_result_by_id(file_id, current_user['email'])
    if not record:
        return jsonify({
            'status': 404,
            'message': '해당 file_id에 대한 결과가 없거나 접근 권한이 없습니다.',
            'result':{
                }
        }), 404

    translated_result_file = record['translated_result_file']

    if not os.path.exists(translated_result_file):
        return jsonify({
            'status': 404,
            'message': '분석 결과 파일이 존재하지 않습니다.',
            'result':{
                }
        }), 404

    try:
        with open(translated_result_file, 'r', encoding='utf-8-sig') as f:
            scan_results = json.load(f)
        return jsonify({
            'status': 200,
            'message': 'success',
            'result': scan_results
        }), 200
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': '파일 읽기 실패 :' + str(e),
            'result':{
                }
        }), 500
