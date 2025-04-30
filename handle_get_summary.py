from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
import json

with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

MONGO_URI = config.get('MONGO_URI')
DB_NAME = config.get('DB_NAME')
COLLECTION_NAME = "scan_results"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_analysis_report(file_id):
    """MongoDB에서 분석 보고서 데이터 가져오기"""
    report = collection.find_one({"file_id": file_id})  # 필드명이 맞는지 확인
    # print("DB Query Result:", report)  # 디버깅용
    return report


def get_summary_report(file_id):
    """취약점 분석 보고서를 요약하여 반환하는 엔드포인트"""
    
    # MongoDB에서 데이터 조회
    db_data = get_analysis_report(file_id)
    if not db_data:
        return jsonify({
            'status': 404,
            'message': 'Report not found',
            'result': None
        }), 404

    json_file_path = db_data.get("translated_result_file")  # MongoDB에서 경로 가져오기
    if not os.path.exists(json_file_path):
        return jsonify({
            'status': 404,
            'message': 'JSON file not found',
            'result': None
        }), 404

    # JSON 파일 로드
    try:
        with open(json_file_path, "r", encoding="utf-8-sig") as file:  # utf-8-sig 사용
            json_data = json.load(file)
    except json.JSONDecodeError as e:
        return jsonify({
            'status': 500,
            'message': f"JSON Decode Error: {str(e)}",
            'result': None
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
        "user_id": None,  # 비회원이므로 null
        "analyzed_at": db_data.get("created_at"),  # MongoDB에서 가져온 분석 날짜/시간
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