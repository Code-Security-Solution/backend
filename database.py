import sqlite3

DB_PATH = "db.sqlite3"

def init_db():
    """SQLite DB 초기화 (테이블 생성)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_results (
            file_id TEXT PRIMARY KEY,
            file_path TEXT NOT NULL,
            result_file TEXT NOT NULL,
            translated_result_file TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_scan_record(file_id, file_path, result_file, translated_result_file):
    """분석 결과 DB에 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scan_results (file_id, file_path, result_file, translated_result_file)
        VALUES (?, ?, ?, ?)
    ''', (file_id, file_path, result_file, translated_result_file))
    conn.commit()
    conn.close()

def get_scan_result_by_id(file_id):
    """file_id로 DB에서 분석 결과 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT file_id, file_path, result_file, translated_result_file FROM scan_results WHERE file_id = ?
    ''', (file_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {'file_id': row[0], 'file_path': row[1], 'result_file': row[2], 'translated_result_file': row[3]}
    return None

# DB 초기화 실행
init_db()