from flask import jsonify
import os
import json
from handle_auth import token_required
from database import get_file_by_id

with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

@token_required
def get_summary_report(current_user, file_id):
    """취약점 분석 보고서를 요약하여 반환하는 엔드포인트"""

    # 데이터베이스에서 파일 정보 조회 (이메일로 소유권 확인)
    db_data = get_file_by_id(file_id, current_user['email'])
    if not db_data:
        return jsonify({
            'status': 404,
            'message': 'Report not found or access denied',
            'result':{
                }
        }), 404

    json_file_path = db_data.get("translated_result_file")
    if not os.path.exists(json_file_path):
        return jsonify({
            'status': 404,
            'message': 'JSON file not found',
            'result':{
                }
        }), 404

    # JSON 파일 로드
    try:
        with open(json_file_path, "r", encoding="utf-8-sig") as file:
            json_data = json.load(file)
    except json.JSONDecodeError as e:
        return jsonify({
            'status': 500,
            'message': f"JSON Decode Error: {str(e)}",
            'result':{
                }
        }), 500

    # 전체 취약점 개수 계산
    results = json_data.get("results", [])
    total_vulnerabilities = len(results)

    # 심각도별 취약점 개수 계산
    severity_summary = {"critical": 0, "error": 0, "warning": 0, "info": 0}
    for item in results:
        severity = item.get("extra", {}).get("severity", "").lower()
        if severity in severity_summary:
            severity_summary[severity] += 1

    # 스캔한 파일 목록
    scanned_files = json_data.get("paths", {}).get("scanned", [])

    # 취약점 목록 정리
    vulnerabilities = []
    for item in results:
        vulnerabilities.append({
            "id": item.get("fingerprint"),
            "file": item.get("path"),
            "line": item.get("start", {}).get("line"),
            "column": item.get("start", {}).get("col"),
            "type": item.get("check_id"),
            "message": item.get("extra", {}).get("message"),
            "severity": item.get("extra", {}).get("severity")
        })

    # 최종 응답 JSON
    summary_report = {
        "user_id": current_user['email'],  # 현재 사용자의 이메일 사용
        "analyzed_at": db_data.get("created_at"),
        "scannedFiles": scanned_files,
        "totalVulnerabilities": total_vulnerabilities,
        "severitySummary": severity_summary,
        "vulnerabilities": vulnerabilities
    }

    return jsonify({
            'status': 200,
            'message': 'success',
            'result':summary_report
        }), 200
