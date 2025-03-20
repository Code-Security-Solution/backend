# backend

## 진행 상황
    
    서버 실행 후
    curl.exe -X POST http://127.0.0.1:5000/scan -F "source_code=@C:\cng\Vulnerable-Code-Snippets\Buffer Overflow\example1.c"
    위와 같이 입력시 json파일이 출력됨.


## 실행 방법

    git clone https://github.com/Code-Security-Solution/backend.git
    
    config.template.json파일에서 CLI_EXECUTABLE 에 Code_Nova_Guardian.exe 의 경로를 입력해야함.
    [ex) "CLI_EXECUTABLE" : "C:\\cng\\Code_Nova_Guardian.exe"]

    cd backend
    
    python -m venv venv
    .\venv\Scripts\activate     # 가상 환경 생성

    pip install flask           # flask 설치

    python main.py