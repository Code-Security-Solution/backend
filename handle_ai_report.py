from flask import jsonify, request
import os
import json
from openai import OpenAI
from database import get_file_by_id, update_file_with_ai_report, detailed_reports_collection, db, get_detailed_report, save_ai_report, get_ai_report
from handle_auth import token_required
from datetime import datetime

# 설정 파일 로드
with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

OPENAI_API_KEY = config.get('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_report(current_user, file_id, fingerprint):
    """AI 리포트 생성"""
    try:
        # 상세 리포트 조회
        detailed_report = get_detailed_report(file_id, fingerprint)
        if not detailed_report:
            return {'status': 404, 'message': '상세 리포트를 찾을 수 없습니다.', 'result': None}

        # 이미 AI 리포트가 생성되어 있으면 400 반환
        if detailed_report.get('ai_report'):
            return {'status': 400, 'message': '이미 AI 리포트가 생성되어 있습니다.', 'result': None}

        # 취약점 정보 추출
        location = detailed_report.get("location", {})
        message = detailed_report.get("message", "")
        code = detailed_report.get("code", "")
        severity = detailed_report.get("severity", "")
        type_info = detailed_report.get("type", "")

        # GPT 프롬프트 생성
        with open('prompts/one_shot_example.txt', 'r', encoding='utf-8') as f:
            example_prompt = f.read()
        prompt = example_prompt + f"""
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
        print(prompt)

        # GPT API 호출
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a security expert analyzing code vulnerabilities."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_report_contents = response.choices[0].message.content

        # ai_report, ai_report_contents 저장
        save_ai_report(file_id, fingerprint, ai_report_contents)

        return {
            'status': 200,
            'message': 'AI 리포트가 성공적으로 생성되었습니다.',
            'result': {
                'ai_report': True,
                'ai_report_contents': ai_report_contents
            }
        }
    except Exception as e:
        print(f"Error generating AI report: {str(e)}")
        return {'status': 500, 'message': f'AI 리포트 생성 중 오류 발생: {str(e)}', 'result': None}

@token_required
def get_ai_report(current_user, file_id, fingerprint=None):
    """저장된 AI 레포트 조회"""
    try:
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
    except Exception as e:
        print(f"Error getting AI report: {str(e)}")
        return jsonify({
            'status': 500,
            'message': 'AI 레포트 조회 중 오류 발생',
            'result': None
        }), 500