from flask import jsonify
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
    return collection.find_one({"file_id": file_id})


def get_detailed_report(file_id):
    db_data = get_analysis_report(file_id)
    if not db_data:
        return jsonify({
            "status": 404,
            "message": "Report not found",
            "result": None
        }), 404

    json_file_path = db_data.get("translated_result_file")
    if not os.path.exists(json_file_path):
        return jsonify({
            "status": 404,
            "message": "JSON file not found",
            "result": None
        }), 404

    try:
        with open(json_file_path, "r", encoding="utf-8-sig") as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        return jsonify({
            "status": 500,
            "message": f"JSON Decode Error: {str(e)}",
            "result": None
        }), 500

    results = json_data.get("results", [])
    if not results:
        return jsonify({
            "status": 404,
            "message": "No vulnerability found in result file",
            "result": None
        }), 404

    match = results[0]  # 첫 번째 취약점만 사용
    file = match.get("path", "")
    start = match.get("start", {})
    end = match.get("end", {})
    check_id = match.get("check_id", "")
    message = match.get("extra", {}).get("message", "")
    severity = match.get("extra", {}).get("severity", "")
    code_snippet = match.get("lines", "").strip()
    metadata = match.get("extra", {}).get("metadata", {})

    references = metadata.get("references", [])
    rule_url = metadata.get("semgrep.dev.rule.url")
    if rule_url and rule_url not in references:
        references.append(rule_url)

    unique_id = f"{file}_{start.get('line', 0)}_{start.get('col', 0)}_{check_id}"

    result = {
        "user_id": None,
        "id": unique_id,
        "file": file,
        "location": {
            "start": {
                "line": start.get("line"),
                "column": start.get("col")
            },
            "end": {
                "line": end.get("line"),
                "column": end.get("col")
            }
        },
        "type": check_id,
        "message": message,
        "severity": severity,
        "suggestion": message,
        "code_snippet": code_snippet,
        "metadata": {
            "cwe": metadata.get("cwe", []),
            "category": metadata.get("category", ""),
            "technology": metadata.get("technology", []),
            "subcategory": metadata.get("subcategory", []),
            "likelihood": metadata.get("likelihood", ""),
            "impact": metadata.get("impact", ""),
            "vulnerability_class": metadata.get("vulnerability_class", [])
        },
        "references": references
    }

    return jsonify({
        "status": 200,
        "message": "success",
        "result": result
    }), 200
