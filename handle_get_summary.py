from flask import jsonify
import os
import json
# token_required 주석 처리
# from handle_auth import token_required
from database import get_file_by_id

with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

RESULT_DIR = 'results'

# token_required 데코레이터 제거
def get_summary_report(file_id):
    """취약점 분석 보고서를 요약하여 반환하는 엔드포인트"""

    # 먼저 DB에서 조회 시도
    db_data = get_file_by_id(file_id)
    json_file_path = None

    if db_data:
        # DB에 기록이 있는 경우 (로그인한 사용자)
        json_file_path = db_data.get("translated_result_file")
    else:
        # DB에 기록이 없는 경우 (비로그인 사용자)
        # 파일 시스템에서 직접 찾기
        temp_file_path = os.path.join(RESULT_DIR, f"{file_id}.json")
        if os.path.exists(temp_file_path):
            json_file_path = temp_file_path

    # 파일을 찾지 못한 경우
    if not json_file_path:
        return jsonify({
            'status': 404,
            'message': '요약 보고서를 찾을 수 없습니다.',
            'result':None
        }), 404

    # 파일이 존재하는지 확인
    if not os.path.exists(json_file_path):
        return jsonify({
            'status': 404,
            'message': 'JSON 파일을 찾을 수 없습니다.',
            'result':None
        }), 404

    # JSON 파일 로드
    try:
        with open(json_file_path, "r", encoding="utf-8-sig") as file:
            json_data = json.load(file)
    except json.JSONDecodeError as e:
        return jsonify({
            'status': 500,
            'message': f"JSON 디코딩 오류: {str(e)}",
            'result':None
        }), 500

    # 전체 취약점 개수 계산
    results = json_data.get("results", [])
    total_vulnerabilities = len(results)

    # 심각도별 취약점 개수 계산
    severity_summary = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
    for item in results:
        severity = item.get("extra", {}).get("severity", "")
        if severity in severity_summary:
            severity_summary[severity] += 1

    # 스캔한 파일 목록
    scanned_files = json_data.get("paths", {}).get("scanned", [])

    # 취약점 목록 정리
    vulnerabilities = []
    for item in results:
        vulnerabilities.append({
            "id": item.get("extra", {}).get("fingerprint"),
            "file": item.get("path"),
            "line": item.get("start", {}).get("line"),
            "column": item.get("start", {}).get("col"),
            "type": item.get("check_id"),
            "message": item.get("extra", {}).get("message"),
            "severity": item.get("extra", {}).get("severity")
        })

    # 파일 생성 시간 정보 (DB가 없는 경우 현재 시간 사용)
    created_at = None
    if db_data:
        created_at = db_data.get("created_at")

    # 최종 응답 JSON
    summary_report = {
        "user_id": "anonymous" if not db_data else db_data.get("user_email", "anonymous"),
        "analyzed_at": created_at,
        "scannedFiles": scanned_files,
        "totalVulnerabilities": total_vulnerabilities,
        "severitySummary": severity_summary,
        "vulnerabilities": vulnerabilities
    }

    return jsonify({
            'status': 200,
            'message': '성공',
            'result':summary_report
        }), 200
