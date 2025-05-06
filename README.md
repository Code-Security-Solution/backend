# Code Nova Guardian Backend

## 프로젝트 소개
Code Nova Guardian은 소스 코드의 보안 취약점을 분석하는 프로그램입니다. RESTful API를 통해 소스 코드 분석, 사용자 인증, 파일 관리 기능을 제공합니다.

## 주요 기능
- 소스 코드 보안 취약점 분석
- 사용자 인증 및 권한 관리
- 분석 결과 저장 및 조회
- 상세 분석 보고서 생성
- 파일 업로드/다운로드 관리

## 기술 스택
- **Backend Framework**: Flask (Python)
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Token)
- **Analysis Tool**: Code Nova Guardian
- **File Management**: Werkzeug
- **Requirements**: Python 3.8+

## 프로젝트 구조
```
/backend
│── main.py                    # Flask 앱 실행 및 엔드포인트 등록
│── handle_auth.py             # 인증 관련 요청 처리
│── handle_scan_request.py     # 코드 분석 요청 처리
│── handle_get_result.py       # 분석 결과 조회 처리
│── handle_get_summary.py      # 요약 보고서 생성 처리
│── handle_get_detail.py       # 상세 분석 보고서 생성 처리
│── handle_files.py            # 파일 관리 요청 처리
│── database.py                # MongoDB 연결 및 데이터 처리
│── config.template.json       # 설정 파일 템플릿
│── .gitignore                 # Git 제외 파일 목록
│── README.md                  # 프로젝트 문서

자동 생성 디렉토리:
│── uploads/                   # 업로드된 소스 코드 파일 저장
│── results/                   # 분석 결과 파일 저장
│── __pycache__/               # Python 캐시 파일
```

## 설치 및 실행

### 1. 사전 요구사항
- Python 3.8 이상
- MongoDB 서버
- Code Nova Guardian 분석 도구

### 2. 설치
```bash
# 저장소 클론
git clone https://github.com/Code-Security-Solution/backend.git
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install flask pymongo pyjwt werkzeug
```

### 3. 설정
1. `config.template.json` 설정
```json
{
    "CLI_EXECUTABLE": "C:/path/to/Code_Nova_Guardian.exe",
    "MONGO_URI": "mongodb://localhost:27017/",
    "DB_NAME": "security_analysis",
    "SECRET_KEY": "your-secret-key-here"
}
```

### 4. 서버 실행
```bash
python main.py
```

## API 문서

### 인증 API
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | 사용자 회원가입 | No |
| POST | `/login` | 사용자 로그인 | No |
| GET | `/user/me` | 현재 사용자 정보 조회 | Yes |

### 분석 API
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/scan` | 소스 코드 분석 요청 | Optional |
| GET | `/scan-result/<file_id>` | 분석 결과 조회 | No |
| GET | `/summary-report/<file_id>` | 요약 보고서 조회 | No |
| GET | `/detail-report/<file_id>` | 상세 분석 보고서 조회 | No |

### 파일 관리 API
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/my-files` | 사용자 파일 목록 조회 | Yes |
| GET | `/download-source/<file_id>` | 원본 소스 파일 다운로드 | Yes |
| GET | `/download-result/<file_id>` | 분석 결과 파일 다운로드 | Yes |
| GET | `/download-translated-result/<file_id>` | 번역된 분석 결과 다운로드 | Yes |
| GET | `/download-all-sources/<file_id>` | 모든 소스 파일 다운로드 (ZIP) | Yes |

## API 응답 형식

### 성공 응답
```json
{
  "status": "success",
  "data": {
    // 응답 데이터
  }
}
```

### 오류 응답
```json
{
  "status": "error",
  "message": "오류 메시지"
}
```

## 상태 코드
- **200**: 성공
- **201**: 리소스 생성 성공
- **400**: 잘못된 요청
- **401**: 인증 실패
- **404**: 리소스 없음
- **500**: 서버 오류

## API 사용 예시

### 회원가입
```bash
curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "username": "홍길동"
  }'
```

### 로그인
```bash
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### 코드 분석 요청
```bash
# 단일 파일 분석
curl -X POST http://127.0.0.1:5000/scan \
  -H "x-access-token: YOUR_TOKEN" \
  -F "source_code=@/path/to/example.c"

# 다중 파일 분석
curl -X POST http://127.0.0.1:5000/scan \
  -H "x-access-token: YOUR_TOKEN" \
  -F "source_code=@/path/to/example1.c" \
  -F "source_code=@/path/to/example2.c"
```

### 분석 결과 조회
```bash
# 분석 결과 조회
curl -X GET http://127.0.0.1:5000/scan-result/FILE_ID

# 요약 보고서 조회
curl -X GET http://127.0.0.1:5000/summary-report/FILE_ID

# 상세 분석 보고서 조회
curl -X GET http://127.0.0.1:5000/detail-report/FILE_ID
```

## 주의사항
1. 인증되지 않은 사용자의 분석 결과는 데이터베이스에 저장되지 않습니다.
2. 민감한 정보가 포함된 소스 코드는 반드시 인증 후 분석을 요청하세요.
3. 분석 도구(Code Nova Guardian)가 올바르게 설치되어 있어야 합니다.
