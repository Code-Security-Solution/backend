# Backend

## 구조

    /backend
    │── main.py                    # Flask 앱 실행 및 엔드포인트 등록
    │── handle_auth.py             # 인증 관련 요청 처리 (/register, /login, /user/me)
    │── handle_scan_request.py     # /scan 요청 처리
    │── handle_get_result.py       # /scan-result 요청 처리
    │── handle_get_summary.py      # /summary-report 요청 처리
    │── handle_files.py            # 파일 다운로드 및 목록 조회 요청 처리
    │── database.py                # MongoDB DB 연결 및 데이터 처리
    │── config.template.json       # 설정 파일
    │── .gitignore                 # Git 제외 파일 목록
    │── README.md                  # README 파일

    아래는 자동 생성됨:
    │── uploads/                   # 업로드된 소스 코드 파일 저장
    │── results/                   # 분석 결과 파일 저장
    │── __pycache__/               # Python 캐시 파일

## API 엔드포인트

### 인증 API
- `POST /register` - 사용자 회원가입 (email, password, username 필수)
- `POST /login` - 사용자 로그인 (토큰 발급)
- `GET /user/me` - 현재 로그인한 사용자 정보 조회 (인증 필요)

### 파일 관리 API (추가 구현 사항)
- `GET /my-files` - 사용자의 파일 목록 조회 (인증 필요)
- `GET /download-source/<file_id>` - 원본 소스 파일 단일 다운로드 (인증 필요)
- `GET /download-all-sources/<file_id>` - 모든 원본 소스 파일 다운로드 (ZIP) (인증 필요)
- `GET /download-result/<file_id>` - 분석 결과 파일 다운로드 (인증 필요)
- `GET /download-translated-result/<file_id>` - 번역된 분석 결과 파일 다운로드 (인증 필요)

### 분석 API
- `POST /scan` - 소스 코드 분석 요청
- `GET /scan-result/<file_id>` - 특정 파일의 분석 결과 조회
- `GET /summary-report/<file_id>` - 특정 파일의 분석 요약 보고서 조회

## 인증 시스템

인증은 일부 API에서 선택 사항이며, 다음 API는 토큰이 필요합니다:
- `/user/me` (사용자 정보 조회)
- `/my-files` (사용자 파일 목록 조회)
- `/download-source/<file_id>` (파일 다운로드)
- `/download-result/<file_id>` (결과 다운로드)
- `/download-translated-result/<file_id>` (번역된 결과 다운로드)
- `/download-all-sources/<file_id>` (모든 소스 다운로드)

다음 API는 토큰 없이 사용할 수 있습니다:
- `/scan` (소스 코드 분석 요청)
- `/scan-result/<file_id>` (분석 결과 조회)
- `/summary-report/<file_id>` (요약 보고서 조회)

로그인 시 발급받은 토큰을 HTTP 헤더 `x-access-token`에 포함시키면 파일과 사용자를 연결하여 관리할 수 있습니다.

**중요**: 로그인하지 않고 분석을 요청하면 분석은 수행되지만, 결과는 데이터베이스에 저장되지 않습니다. 그러나 파일 시스템에는 결과 파일이 생성되므로, 응답으로 받은 `file_id`를 사용하여 `/scan-result/<file_id>`와 `/summary-report/<file_id>` API를 통해 결과를 확인할 수 있습니다. 서버를 재시작하거나 시간이 경과하여 임시 파일이 삭제될 경우에는 결과를 조회할 수 없게 됩니다.

## 실행 방법

1. 사전 준비
   - MongoDB 실행
   - Code_Nova_Guardian 설치

2. 설정
   ```
   git clone https://github.com/Code-Security-Solution/backend.git
   cd backend
   ```

   - `config.template.json` 파일 설정값 변경:
     - `CLI_EXECUTABLE`: Code_Nova_Guardian.exe의 경로 설정
     - `SECRET_KEY`: 임의의 비밀 키 설정 (JWT 토큰 생성용)

3. 가상 환경 설정 및 의존성 설치
   ```
   python -m venv venv
   .\venv\Scripts\activate     # Windows
   # source venv/bin/activate  # Linux/Mac

   pip install flask pymongo pyjwt werkzeug
   ```

4. 서버 실행
   ```
   python main.py
   ```

## API 사용 예시

### 회원가입
```
# 모든 필수 항목 포함 회원가입
curl -X POST http://127.0.0.1:5000/register -H "Content-Type: application/json" -d "{\"email\":\"user@example.com\",\"password\":\"password123\",\"username\":\"홍길동\"}"
```

### 로그인
```
curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d "{\"email\":\"user@example.com\",\"password\":\"password123\"}"
```

### 사용자 정보 조회 (토큰 필요)
```
curl -X GET http://127.0.0.1:5000/user/me -H "x-access-token: YOUR_TOKEN"
```

### 코드 분석 요청 (토큰 선택 사항)
```
# 토큰 있음 (로그인 사용자로 분석, 데이터베이스에 저장됨)
curl -X POST http://127.0.0.1:5000/scan -H "x-access-token: YOUR_TOKEN" -F "source_code=@C:\path\to\example1.c"

# 토큰 없음 (익명 사용자로 분석, 데이터베이스에 저장되지 않음)
curl -X POST http://127.0.0.1:5000/scan -F "source_code=@C:\path\to\example1.c"

# 다중 파일 분석
curl -X POST http://127.0.0.1:5000/scan -F "source_code=@C:\path\to\example1.c" -F "source_code=@C:\path\to\example2.c"
```

### 분석 결과 조회 (토큰 불필요)
```
curl -X GET http://127.0.0.1:5000/scan-result/FILE_ID
```

### 분석 요약 보고서 조회 (토큰 불필요)
```
curl -X GET http://127.0.0.1:5000/summary-report/FILE_ID
```

### 파일 다운로드 (추가 구현 사항/토큰 필요)
```
# 분석 결과 파일 다운로드
curl -X GET http://127.0.0.1:5000/download-result/FILE_ID -H "x-access-token: YOUR_TOKEN" -o result.json

# 원본 소스 파일 다운로드
curl -X GET http://127.0.0.1:5000/download-source/FILE_ID -H "x-access-token: YOUR_TOKEN" -o source.c

# 번역된 분석 결과 파일 다운로드
curl -X GET http://127.0.0.1:5000/download-translated-result/FILE_ID -H "x-access-token: YOUR_TOKEN" -o translated_result.json

# 모든 원본 소스 파일 다운로드 (ZIP)
curl -X GET http://127.0.0.1:5000/download-all-sources/FILE_ID -H "x-access-token: YOUR_TOKEN" -o all_sources.zip
```

### 사용자 파일 목록 조회 (토큰 필요)
```
curl -X GET http://127.0.0.1:5000/my-files -H "x-access-token: YOUR_TOKEN"
```

## 상태 코드

- **200**: 성공
- **201**: 리소스 생성 성공 (회원가입 등)
- **400**: 잘못된 요청
- **401**: 인증 실패
- **404**: 리소스 없음
- **500**: 서버 오류
