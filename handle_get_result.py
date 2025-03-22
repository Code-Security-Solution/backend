import os
import json
from flask import jsonify
from database import get_scan_result_by_id

def get_scan_result(file_id):
    """
    GET 요청: 특정 file_id의 번역된 분석 결과 JSON 반환
    /scan-result/<file_id>
    """
    
    record = get_scan_result_by_id(file_id)
    if not record:
        return jsonify({'error': '해당 file_id에 대한 결과가 없습니다.'}), 404
    
    translated_result_file = record['translated_result_file']

    if not os.path.exists(translated_result_file):
        return jsonify({'error': '분석 결과 파일이 존재하지 않습니다.'}), 404
    
    try:
        with open(translated_result_file, 'r', encoding='utf-8-sig') as f:
            scan_results = json.load(f)
        return jsonify({'scan_results': scan_results})
    except Exception as e:
        return jsonify({'error': '파일 읽기 실패', 'details': str(e)}), 500