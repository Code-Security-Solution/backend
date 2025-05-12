from flask import Flask, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
import zipfile
import tempfile
from handle_scan_request import scan_code
from handle_get_result import get_scan_result
from handle_get_summary import get_summary_report
from handle_get_detail import get_detailed_report
from handle_auth import token_required, register_user_handler, login_handler, get_user_info
from handle_files import download_source_handler, download_result_handler, download_translated_result_handler, download_all_sources_handler, my_files_handler
from database import register_user, get_user_by_email, get_user_files, get_file_by_id, json_serialize
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
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
app.json_encoder = MongoJSONEncoder  # 커스텀 JSONEncoder 설정

# URL 라우팅 설정
app.add_url_rule('/scan', view_func=scan_code, methods=['POST'])
app.add_url_rule('/scan-result/<file_id>', view_func=get_scan_result, methods=['GET'])
app.add_url_rule('/summary-report/<file_id>', view_func=get_summary_report, methods=['GET'])
app.add_url_rule('/detail-report/<file_id>', view_func=get_detailed_report, methods=['GET'])

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
