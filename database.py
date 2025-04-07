from pymongo import MongoClient
import json
import os
from flask import request, jsonify
from bson import ObjectId
from datetime import datetime

def json_serialize(obj):
    """MongoDB 객체를 JSON으로 직렬화하는 함수"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

MONGO_URI = config.get('MONGO_URI')
DB_NAME = config.get('DB_NAME')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# 컬렉션 초기화 및 인덱스 설정
users_collection = db["users"]
files_collection = db["files"]

# email 필드에 유니크 인덱스 설정
users_collection.create_index("email", unique=True)

# 파일 업로드 기록 저장
def insert_scan_record(user_email, file_id, file_paths, result_file, translated_result_file):
    """분석 결과 DB에 저장"""
    files_collection.insert_one({
        "email": user_email,
        "file_id": file_id,
        "file_paths": file_paths,
        "result_file": result_file,
        "translated_result_file": translated_result_file,
        "created_at": db.command("serverStatus")["localTime"]
    })

# 회원가입 (이메일 중복 체크 후 저장)
def register_user(email, password_hash, username=None):
    if users_collection.find_one({"email": email}):
        return False  # 이미 존재하는 이메일
    users_collection.insert_one({
        "email": email,
        "password": password_hash,
        "username": username
    })
    return True

# 유저 정보 조회 (로그인 시 사용)
def get_user_by_email(email):
    return users_collection.find_one({"email": email})

# 파일 업로드 기록 저장
def get_user_files(email):
    return list(files_collection.find({"email": email}))

# 특정 파일 ID와 이메일로 파일 조회 (파일 소유권 확인)
def get_file_by_id(file_id, email):
    return files_collection.find_one({"file_id": file_id, "email": email})

def get_scan_result_by_id(file_id, email):
    """특정 file_id와 이메일로 스캔 결과 조회 (파일 소유권 확인)"""
    # 사용자의 파일 소유권 확인
    file_info = get_file_by_id(file_id, email)
    if not file_info:
        return None

    # 변환된 결과 파일 정보 반환
    return {
        "file_id": file_id,
        "email": email,
        "result_file": file_info.get("result_file"),
        "translated_result_file": file_info.get("translated_result_file")
    }
