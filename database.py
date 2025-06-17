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
detailed_reports_collection = db["detailed_reports"]  # 상세 보고서를 위한 새로운 컬렉션

# email 필드에 유니크 인덱스 설정
users_collection.create_index("email", unique=True)
# file_id에 인덱스 설정
detailed_reports_collection.create_index("file_id")

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

# 특정 파일 ID로 파일 조회 (이메일 매개변수 선택 사항)
def get_file_by_id(file_id, email=None):
    if email:
        # 이메일이 제공된 경우 소유권 확인
        return files_collection.find_one({"file_id": file_id, "email": email})
    else:
        # 이메일이 제공되지 않은 경우 file_id로만 조회
        return files_collection.find_one({"file_id": file_id})

def get_scan_result_by_id(file_id, email=None):
    """특정 file_id로 스캔 결과 조회 (이메일 매개변수 선택 사항)"""
    # 파일 정보 조회
    file_info = get_file_by_id(file_id, email)
    if not file_info:
        return None

    # 변환된 결과 파일 정보 반환
    return {
        "file_id": file_id,
        "user_email": file_info.get("email", "anonymous"),
        "result_file": file_info.get("result_file"),
        "translated_result_file": file_info.get("translated_result_file")
    }

def update_file_with_ai_report(file_id, fingerprint, ai_report):
    """AI 레포트를 파일 정보에 업데이트"""
    files_collection.update_one(
        {"file_id": file_id},
        {
            "$set": {
                f"ai_reports.{fingerprint}": ai_report
            }
        }
    )

def save_detailed_report(file_id, detailed_report):
    """상세 리포트를 MongoDB에 저장 (필수 필드 보장, fingerprint는 반드시 외부에서 받아야 함)"""
    try:
        # fingerprint가 반드시 있어야 함
        if 'fingerprint' not in detailed_report or not detailed_report['fingerprint']:
            raise ValueError('fingerprint 값이 반드시 필요합니다.')
        # 필수 필드 목록
        required_fields = [
            'file_id', 'fingerprint', 'ai_report', 'ai_report_contents', 'code', 'file', 'id', 'location',
            'message', 'metadata', 'references', 'severity', 'suggestion', 'type', 'user_id', 'created_at'
        ]
        # 기본값 세팅
        for field in required_fields:
            if field not in detailed_report:
                if field == 'ai_report':
                    detailed_report[field] = False
                elif field == 'ai_report_contents':
                    detailed_report[field] = None
                elif field == 'created_at':
                    detailed_report[field] = datetime.utcnow()
                else:
                    detailed_report[field] = None
        detailed_report['file_id'] = file_id
        # upsert: created_at은 새 문서에만 추가
        existing = detailed_reports_collection.find_one({'file_id': file_id, 'fingerprint': detailed_report['fingerprint']})
        if existing:
            # 기존 문서면 created_at을 덮어쓰지 않음
            detailed_report['created_at'] = existing.get('created_at', detailed_report['created_at'])
        result = detailed_reports_collection.update_one(
            {
                'file_id': file_id,
                'fingerprint': detailed_report['fingerprint']
            },
            {'$set': detailed_report},
            upsert=True
        )
        return result.acknowledged
    except Exception as e:
        print(f"Error saving detailed report: {str(e)}")
        return False

def get_detailed_report(file_id, fingerprint):
    """MongoDB에서 상세 리포트 조회"""
    try:
        report = detailed_reports_collection.find_one({
            'file_id': file_id,
            'fingerprint': fingerprint
        })
        return report
    except Exception as e:
        print(f"Error getting detailed report: {str(e)}")
        return None

def reset_ai_report(file_id, fingerprint):
    """AI 리포트 상태 초기화"""
    try:
        result = detailed_reports_collection.update_one(
            {
                'file_id': file_id,
                'fingerprint': fingerprint
            },
            {
                '$set': {
                    'ai_report': False,
                    'ai_report_contents': None
                }
            }
        )
        return result.acknowledged
    except Exception as e:
        print(f"Error resetting AI report: {str(e)}")
        return False

def save_ai_report(file_id, fingerprint, ai_report_contents):
    """AI 리포트 저장"""
    try:
        result = detailed_reports_collection.update_one(
            {
                'file_id': file_id,
                'fingerprint': fingerprint
            },
            {
                '$set': {
                    'ai_report': True,
                    'ai_report_contents': ai_report_contents
                }
            }
        )
        return result.acknowledged
    except Exception as e:
        print(f"Error saving AI report: {str(e)}")
        return False

def get_ai_report(file_id, fingerprint):
    """AI 리포트 조회"""
    try:
        report = detailed_reports_collection.find_one(
            {
                'file_id': file_id,
                'fingerprint': fingerprint
            },
            {'ai_report': 1, 'ai_report_contents': 1, '_id': 0}
        )
        return report
    except Exception as e:
        print(f"Error getting AI report: {str(e)}")
        return None
