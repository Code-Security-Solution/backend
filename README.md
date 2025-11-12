[Code-Security-Solution/backend](https://github.com/Code-Security-Solution/backend) 레포지토리를 분석하여 개선된 README 파일을 작성했습니다.

***

# Code Nova Guardian Backend

> AI 기반 소스 코드 보안 취약점 분석 시스템의 백엔드 API 서버

## 📋 프로젝트 개요

Code Nova Guardian Backend는 소스 코드의 보안 취약점을 자동으로 분석하고, AI를 활용하여 상세한 취약점 분석 리포트를 제공하는 RESTful API 서버입니다. Code Nova Guardian CLI 분석 도구와 연동하여 C/C++ 코드의 보안 취약점을 탐지하고, OpenAI GPT 모델을 통해 취약점에 대한 분석, 수정 방안, 예방책을 제시합니다.

## ✨ 주요 기능

### 코드 분석
- **소스 코드 보안 취약점 스캔**: Code Nova Guardian CLI를 통한 정적 코드 분석
- **다중 파일 지원**: 여러 파일을 동시에 업로드하여 일괄 분석
- **실시간 분석 결과 제공**: JSON 형식의 상세 분석 결과 반환

### AI 리포트 생성
- **AI 기반 취약점 분석**: OpenAI GPT-4를 활용한 취약점 상세 분석
- **취약점별 맞춤 리포트**: 각 취약점에 대한 분석, 코드 수정 방안, 예방책 제공
- **One-shot Learning**: 프롬프트 엔지니어링을 통한 일관된 분석 품질

### 사용자 관리
- **JWT 기반 인증**: 안전한 토큰 기반 사용자 인증
- **사용자별 분석 이력 관리**: 분석한 파일 및 결과 이력 조회
- **권한 기반 접근 제어**: 인증된 사용자만 특정 기능 접근 가능

### 파일 관리
- **분석 파일 업로드/다운로드**: 원본 소스 코드 및 분석 결과 파일 관리
- **다국어 결과 제공**: 영문 및 한글 번역된 분석 결과 지원
- **ZIP 아카이브 다운로드**: 여러 소스 파일을 압축하여 한번에 다운로드

## 🛠 기술 스택

| 카테고리 | 기술 |
|---------|------|
| **Backend** | Flask (Python 3.8+) |
| **Database** | MongoDB |
| **Authentication** | JWT (PyJWT) |
| **AI/ML** | OpenAI GPT-4.1-mini |
| **Security** | Werkzeug Security |
| **CORS** | Flask-CORS |
| **Analysis Tool** | Code Nova Guardian CLI |

## 📁 프로젝트 구조

```
backend/
├── main.py                      # Flask 앱 진입점 및 라우팅 설정
├── database.py                  # MongoDB 연결 및 데이터 CRUD 작업
├── handle_auth.py               # JWT 인증 및 사용자 관리
├── handle_scan_request.py       # 코드 스캔 요청 처리
├── handle_get_result.py         # 스캔 결과 조회
├── handle_get_summary.py        # 요약 보고서 생성
├── handle_get_detail.py         # 상세 취약점 리포트 조회
├── handle_ai_report.py          # AI 기반 취약점 분석 리포트 생성
├── handle_files.py              # 파일 업로드/다운로드 관리
├── config.template.json         # 설정 파일 템플릿
├── prompts/
│   └── one_shot_example.txt     # AI 프롬프트 템플릿
├── uploads/                     # 업로드된 소스 코드 (자동 생성)
└── results/                     # 분석 결과 파일 (자동 생성)
```

## 🚀 설치 및 실행

### 사전 요구사항

- Python 3.8 이상
- MongoDB 서버 (로컬 또는 Atlas)
- Code Nova Guardian CLI 분석 도구
- OpenAI API 키

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/Code-Security-Solution/backend.git
cd backend

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# 3. 의존성 설치
pip install flask pymongo pyjwt werkzeug flask-cors openai
```

### 설정

`config.template.json`을 `config.json`으로 복사하고 설정값을 입력합니다.

```json
{
    "CLI_EXECUTABLE": "C:/path/to/Code_Nova_Guardian.exe",
    "MONGO_URI": "mongodb://localhost:27017/",
    "DB_NAME": "security_analysis",
    "SECRET_KEY": "your-jwt-secret-key-here",
    "OPENAI_API_KEY": "your-openai-api-key-here"
}
```

### 실행

```bash
python main.py
```

서버는 `http://0.0.0.0:5000`에서 실행됩니다.

## 📡 API 엔드포인트

### 인증 API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | 사용자 회원가입 | ❌ |
| POST | `/login` | 로그인 및 토큰 발급 | ❌ |
| GET | `/user/me` | 현재 사용자 정보 조회 | ✅ |

### 분석 API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/scan` | 소스 코드 분석 요청 | 선택 |
| GET | `/scan-result/<file_id>` | 분석 결과 조회 | ❌ |
| GET | `/summary-report/<file_id>` | 요약 보고서 조회 | ❌ |
| GET | `/detail-report/<file_id>` | 상세 취약점 리포트 조회 | ❌ |

### AI 리포트 API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/ai-report/<file_id>/<fingerprint>` | AI 리포트 생성 | ✅ |
| GET | `/ai-report/<file_id>/<fingerprint>` | AI 리포트 조회 | ✅ |
| POST | `/reset-ai-report/<file_id>` | AI 리포트 초기화 | ✅ |

### 파일 관리 API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/my-files` | 사용자 파일 목록 조회 | ✅ |
| GET | `/download-source/<file_id>` | 원본 소스 다운로드 | ✅ |
| GET | `/download-result/<file_id>` | 분석 결과 다운로드 | ✅ |
| GET | `/download-translated-result/<file_id>` | 번역된 결과 다운로드 | ✅ |
| GET | `/download-all-sources/<file_id>` | 모든 소스 ZIP 다운로드 | ✅ |

### 시스템 API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | 서버 상태 체크 (EC2 헬스 체크용) | ❌ |

## 💡 사용 예시

### 회원가입

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "username": "홍길동"
  }'
```

### 로그인

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**응답 예시:**
```json
{
  "status": 200,
  "message": "로그인 성공",
  "result": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "email": "user@example.com",
      "username": "홍길동"
    }
  }
}
```

### 코드 스캔 요청

```bash
# 단일 파일 분석
curl -X POST http://localhost:5000/scan \
  -H "x-access-token: YOUR_JWT_TOKEN" \
  -F "source_code=@/path/to/vulnerable.c"

# 다중 파일 분석
curl -X POST http://localhost:5000/scan \
  -H "x-access-token: YOUR_JWT_TOKEN" \
  -F "source_code=@file1.c" \
  -F "source_code=@file2.c" \
  -F "source_code=@file3.c"
```

### 분석 결과 조회

```bash
curl -X GET http://localhost:5000/scan-result/abc123def456
```

### AI 리포트 생성

```bash
curl -X POST "http://localhost:5000/ai-report/abc123def456/fingerprint_value" \
  -H "x-access-token: YOUR_JWT_TOKEN"
```

### AI 리포트 조회

```bash
curl -X GET "http://localhost:5000/ai-report/abc123def456/fingerprint_value" \
  -H "x-access-token: YOUR_JWT_TOKEN"
```

## 🗄 데이터베이스 스키마

### users 컬렉션
```json
{
  "email": "user@example.com",
  "password": "hashed_password",
  "username": "홍길동"
}
```

### files 컬렉션
```json
{
  "email": "user@example.com",
  "file_id": "unique_file_id",
  "file_paths": ["path/to/file1.c", "path/to/file2.c"],
  "result_file": "path/to/result.json",
  "translated_result_file": "path/to/translated_result.json",
  "created_at": "2025-11-12T13:32:00Z"
}
```

### detailed_reports 컬렉션
```json
{
  "file_id": "unique_file_id",
  "fingerprint": "vulnerability_fingerprint",
  "code": "vulnerable code snippet",
  "file": "filename.c",
  "location": {"line": 42, "column": 10},
  "message": "Buffer overflow detected",
  "severity": "high",
  "type": "CWE-120",
  "ai_report": true,
  "ai_report_contents": "AI generated analysis...",
  "created_at": "2025-11-12T13:32:00Z"
}
```

## 🔒 보안 고려사항

- **JWT 인증**: 모든 민감한 API는 JWT 토큰 기반 인증 필요
- **비밀번호 해싱**: Werkzeug의 `generate_password_hash`를 사용한 안전한 비밀번호 저장
- **CORS 설정**: 허용된 도메인만 API 접근 가능
- **익명 분석 제한**: 인증되지 않은 사용자의 분석 결과는 DB에 저장되지 않음
- **파일 접근 제어**: 사용자는 본인이 업로드한 파일만 다운로드 가능

## ⚠️ 주의사항

1. **인증되지 않은 분석**: 토큰 없이 `/scan`을 호출하면 분석은 수행되지만 결과가 DB에 저장되지 않습니다.
2. **민감 정보 보호**: 중요한 소스 코드는 반드시 인증 후 분석을 요청하세요.
3. **CLI 도구 설치**: Code Nova Guardian CLI가 올바르게 설치되어 있어야 합니다.
4. **OpenAI API 키**: AI 리포트 생성을 위해서는 유효한 OpenAI API 키가 필요합니다.
5. **프로덕션 배포**: 프로덕션 환경에서는 `debug=False`로 설정하고 HTTPS를 사용하세요.

## 🌐 프로덕션 배포

프로덕션 환경에서는 다음 설정이 적용됩니다:

- **CORS 허용 도메인**: `https://www.codenovaguardian.site`
- **호스트**: `0.0.0.0:5000` (EC2 인스턴스)
- **Health Check**: `/health` 엔드포인트로 서버 상태 모니터링

***

**Built with ❤️ by Code Security Solution Team**
