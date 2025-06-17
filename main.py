from flask import Flask, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
import zipfile
import tempfile
from flask_cors import CORS
from handle_scan_request import scan_code
from handle_get_result import get_scan_result
from handle_get_summary import get_summary_report
from handle_get_detail import get_detailed_report
from handle_ai_report import generate_ai_report, get_ai_report
from handle_auth import token_required, register_user_handler, login_handler, get_user_info
from handle_files import download_source_handler, download_result_handler, download_translated_result_handler, download_all_sources_handler, my_files_handler
from database import register_user, get_user_by_email, get_user_files, get_file_by_id, json_serialize, reset_ai_report
import json
from bson import ObjectId

# 설정 파일 로드
with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

# 커스텀 JSONEncoder 정의
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json_serialize(obj)
        except TypeError:
            return super(MongoJSONEncoder, self).default(obj)

app = Flask(__name__)

# CORS 설정
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "https://www.codenovaguardian.site"],  # 프론트엔드 주소
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "x-access-token"]
    }
})

app.config['SECRET_KEY'] = config.get('SECRET_KEY')
app.json_encoder = MongoJSONEncoder  # 커스텀 JSONEncoder 설정

# EC2 health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'Healthy'}), 200

# URL 라우팅 설정
app.add_url_rule('/scan', view_func=scan_code, methods=['POST'])
app.add_url_rule('/scan-result/<file_id>', view_func=get_scan_result, methods=['GET'])
app.add_url_rule('/summary-report/<file_id>', view_func=get_summary_report, methods=['GET'])
app.add_url_rule('/detail-report/<file_id>', view_func=get_detailed_report, methods=['GET'])

# AI 레포트 관련 라우팅
app.add_url_rule('/ai-report/<file_id>', view_func=generate_ai_report, methods=['POST'])
app.add_url_rule('/ai-report/<file_id>', view_func=get_ai_report, methods=['GET'])

# 인증 관련 라우팅
app.add_url_rule('/register', view_func=register_user_handler, methods=['POST'])
app.add_url_rule('/login', view_func=login_handler, methods=['POST'])
app.add_url_rule('/user/me', view_func=get_user_info, methods=['GET'])

# 파일 관리 관련 라우팅
app.add_url_rule('/my-files', view_func=my_files_handler, methods=['GET'])
app.add_url_rule('/download-source/<file_id>', view_func=download_source_handler, methods=['GET'])
app.add_url_rule('/download-result/<file_id>', view_func=download_result_handler, methods=['GET'])
app.add_url_rule('/download-translated-result/<file_id>', view_func=download_translated_result_handler, methods=['GET'])
app.add_url_rule('/download-all-sources/<file_id>', view_func=download_all_sources_handler, methods=['GET'])

# AI 리포트 초기화 엔드포인트
@app.route('/reset-ai-report/<file_id>', methods=['POST'])
@token_required
def reset_ai_report_handler(current_user, file_id):
    """AI 리포트 상태를 초기화하는 엔드포인트"""
    try:
        reset_ai_report(file_id)
        return jsonify({
            'status': 200,
            'message': 'AI 리포트가 성공적으로 초기화되었습니다.',
            'result': None
        }), 200
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'AI 리포트 초기화 중 오류 발생: {str(e)}',
            'result': None
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
