from pymongo import MongoClient
import json

with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

MONGO_URI = config.get('MONGO_URI')
DB_NAME = config.get('DB_NAME')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
scan_results_collection = db['scan_results']

def insert_scan_record(file_id, file_paths, result_file, translated_result_file):
    """분석 결과 DB에 저장"""
    scan_results_collection.insert_one({
        "file_id": file_id,
        "file_paths": file_paths,
        "result_file": result_file,
        "translated_result_file": translated_result_file,
        "created_at": db.command("serverStatus")["localTime"]
    })

def get_scan_result_by_id(file_id):
    """MongoDB에서 file_id로 검색"""
    result = scan_results_collection.find_one({"file_id": file_id}, {"_id": 0})
    return result