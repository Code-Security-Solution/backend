# backend

## 구조

/bacbend
│── main.py                 # Flask 앱 실행 및 엔드포인트 등록
│── handle_scan_request.py   # /scan 요청 처리
│── handle_get_result.py     # /scan-result 요청 처리
│── database.py              # DB 연결
│── config.json              # 설정 파일 -> config.template.json을 변경해야함.

아래는 자동 생성됨.
│── uploads/                 # 업로드된 소스 코드 파일 저장
│── results/                 # 분석 결과 파일 저장
│── db.sqlite3               # SQLite 데이터베이스


## 진행 상황
    
    서버 실행 후
    curl -X POST http://127.0.0.1:5000/scan -F "source_code=@C:\cng\Vulnerable-Code-Snippets\Buffer Overflow\example1.c"
    위와 같이 요청시 취약점 분석 후 json파일로 저장함.
    uploads 폴더에 피분석 소스코드 파일 저장됨.
    분석 결과는 results 폴더에 저장됨.

    curl -X GET http://127.0.0.1:5000/scan-result/file_id
    위와 같이 요청시 최근 분석 후 저장된 code-scan-result_translated.json 파일을 가져옴.
    


## 실행 방법

    git clone https://github.com/Code-Security-Solution/backend.git
    
    config.template.json파일에서 CLI_EXECUTABLE 에 Code_Nova_Guardian.exe 의 경로를 입력해야함.
    그리고 config.json 으로 이름 변경해야함.
    [ex) "CLI_EXECUTABLE" : "C:\\cng\\Code_Nova_Guardian.exe"]

    cd backend
    
    python -m venv venv
    .\venv\Scripts\activate     # 가상 환경 생성

    pip install flask           # flask 설치

    python main.py


    서버 실행 후 아래와 같이 요청
    curl -X POST http://127.0.0.1:5000/scan -F "source_code=@C:\cng\Vulnerable-Code-Snippets\Buffer Overflow\example1.c"
    curl -X GET http://127.0.0.1:5000/scan-result/file_id
