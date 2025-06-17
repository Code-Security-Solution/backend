from flask import jsonify, request
import os
import json
from openai import OpenAI
from database import get_file_by_id, update_file_with_ai_report, detailed_reports_collection, db
from handle_auth import token_required

# 설정 파일 로드
with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

OPENAI_API_KEY = config.get('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

@token_required
def generate_ai_report(current_user, file_id, fingerprint=None):
    """AI 레포트 생성 및 저장"""
    # 상세 보고서 조회
    detailed_report = detailed_reports_collection.find_one({"file_id": file_id})
    if not detailed_report:
        return jsonify({
            'status': 404,
            'message': '상세 보고서를 찾을 수 없습니다.',
            'result': None
        }), 404

    # 이미 AI 리포트가 있는지 확인
    if detailed_report.get("ai_report", False):
        return jsonify({
            'status': 400,
            'message': '이미 AI 리포트가 생성되어 있습니다.',
            'result': detailed_report.get("ai_report_contents")
        }), 400

    # 취약점 정보 추출
    report_data = detailed_report.get("report", {})
    code = report_data.get("code", "")
    location = report_data.get("location", {})
    message = report_data.get("message", "")
    severity = report_data.get("severity", "")
    type_info = report_data.get("type", "")

    # GPT 프롬프트 생성
    prompt = f"""
다음 취약점에 대한 분석과 해결 방안을 제시해주세요:

위치: {location}
메시지: {message}

취약점이 발생한 코드:
{code}

다음 세 가지 항목에 대해 간단히 설명해주세요:
1. 취약점 분석: 이 취약점이 어떤 위험을 초래할 수 있는지 간단히 설명
2. 코드 수정 방안: 취약점을 해결하기 위한 간단한 코드 수정 방법 제시
3. 예방책: 앞으로 이런 취약점을 방지하기 위한 방법 제시

각 항목은 명확하고 간단하게 작성해주세요.
"""

    try:
        # GPT API 호출
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a security expert analyzing code vulnerabilities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        # AI 리포트 생성
        ai_report = {
            "vulnerability_analysis": response.choices[0].message.content,
            "generated_at": db.command("serverStatus")["localTime"]
        }

        # AI 리포트 저장
        detailed_reports_collection.update_one(
            {"file_id": file_id},
            {
                "$set": {
                    "ai_report": True,
                    "ai_report_contents": ai_report
                }
            }
        )

        return jsonify({
            'status': 200,
            'message': 'AI 리포트가 성공적으로 생성되었습니다.',
            'result': ai_report
        }), 200

    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'AI 리포트 생성 중 오류 발생: {str(e)}',
            'result': None
        }), 500

@token_required
def get_ai_report(current_user, file_id, fingerprint=None):
    """저장된 AI 레포트 조회"""
    # 파일 정보 조회 (현재 사용자의 파일만 조회)
    file_info = get_file_by_id(file_id, current_user['email'])
    if not file_info:
        return jsonify({
            'status': 404,
            'message': '파일을 찾을 수 없거나 접근 권한이 없습니다.',
            'result': None
        }), 404

    # AI 레포트 정보 조회
    ai_reports = file_info.get('ai_reports', {})
    if fingerprint:
        ai_report = ai_reports.get(fingerprint)
    else:
        # fingerprint가 지정되지 않은 경우 첫 번째 레포트 반환
        ai_report = next(iter(ai_reports.values())) if ai_reports else None

    if not ai_report:
        return jsonify({
            'status': 404,
            'message': 'AI 레포트를 찾을 수 없습니다.',
            'result': {
                'has_ai_report': False
            }
        }), 404

    return jsonify({
        'status': 200,
        'message': 'AI 레포트 조회 성공',
        'result': {
            'ai_report': ai_report,
            'has_ai_report': True
        }
    }), 200