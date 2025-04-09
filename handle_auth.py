from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from database import register_user, get_user_by_email
import json

# 설정 파일 로드
with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

SECRET_KEY = config.get('SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': '토큰이 필요합니다!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = get_user_by_email(data['email'])
            if not current_user:
                return jsonify({'message': '유효하지 않은 토큰입니다!'}), 401
        except Exception as e:
            print(f"토큰 검증 오류: {str(e)}")  # 디버깅용 로그 추가
            return jsonify({'message': f'토큰이 유효하지 않습니다! 오류: {str(e)}'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def register_user_handler():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({'message': '이메일과 비밀번호를 입력해주세요!'}), 400

    password_hash = generate_password_hash(password)

    if register_user(email, password_hash):
        return jsonify({'message': '회원가입 성공!'}), 201
    else:
        return jsonify({'message': '이미 존재하는 이메일입니다!'}), 400

def login_handler():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = get_user_by_email(email)
    if user and check_password_hash(user['password'], password):
        token = jwt.encode({'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                        SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': '이메일 또는 비밀번호가 올바르지 않습니다!'}), 401
