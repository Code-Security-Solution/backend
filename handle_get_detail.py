from flask import jsonify, request
import os
import json
from database import get_file_by_id, save_detailed_report

with open('config.json', 'rt', encoding='utf-8') as file:
    config = json.load(file)

RESULT_DIR = 'results'

def get_detailed_report(file_id):
    """특정 파일의 취약점 상세 정보를 반환하는 엔드포인트"""

    # URL 파라미터에서 fingerprint 가져오기
    target_fingerprint = request.args.get('fingerprint')
    
    # 디버깅을 위한 print 문 추가
    print(f"[DEBUG] get_detailed_report 실행 - file_id: {file_id}, target_fingerprint: {target_fingerprint}")

    # 먼저 DB에서 조회 시도
    record = get_file_by_id(file_id)
    print(f"[DEBUG] DB 조회 결과: {record}")
    translated_result_file = None

    if record:
        # DB에 기록이 있는 경우 (로그인한 사용자)
        translated_result_file = record.get('translated_result_file')
        print(f"[DEBUG] DB에서 찾은 파일 경로: {translated_result_file}")
    else:
        # DB에 기록이 없는 경우 (비로그인 사용자)
        # 파일 시스템에서 직접 찾기
        temp_file_path = os.path.join(RESULT_DIR, f"{file_id}_translated.json")
        print(f"[DEBUG] 파일 시스템에서 찾는 경로: {temp_file_path}")
        if os.path.exists(temp_file_path):
            translated_result_file = temp_file_path
            print(f"[DEBUG] 파일 존재함: {temp_file_path}")
        else:
            print(f"[DEBUG] 파일 존재하지 않음: {temp_file_path}")

            # 결과 폴더의 모든 파일 목록 출력 (디버깅용)
            print(f"[DEBUG] results 폴더의 파일 목록:")
            for filename in os.listdir(RESULT_DIR):
                print(f"  - {filename}")

    # 파일을 찾지 못한 경우
    if not translated_result_file:
        print(f"[DEBUG] 파일 경로를 찾지 못함")
        return jsonify({
            "status": 404,
            "message": "상세 보고서를 찾을 수 없습니다.",
            "result": None
        }), 404

    # 파일이 존재하는지 확인
    if not os.path.exists(translated_result_file):
        print(f"[DEBUG] 파일이 존재하지 않음: {translated_result_file}")
        return jsonify({
            "status": 404,
            "message": "JSON 파일을 찾을 수 없습니다.",
            "result": None
        }), 404

    try:
        with open(translated_result_file, "r", encoding="utf-8-sig") as f:
            json_data = json.load(f)
            print(f"[DEBUG] JSON 파일 로드 성공")
            # 파일 내용 출력 (디버깅용)
            print(f"[DEBUG] JSON 파일 내용 미리보기:")
            print(json.dumps(json_data, ensure_ascii=False, indent=2)[:500] + "...")
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON 디코딩 오류: {str(e)}")
        return jsonify({
            "status": 500,
            "message": f"JSON 디코딩 오류: {str(e)}",
            "result": None
        }), 500

    results = json_data.get("results", [])

    print(f"[DEBUG] 결과 목록: {results}")
    if not results:
        print(f"[DEBUG] 결과 파일에 취약점 없음")
        return jsonify({
            "status": 404,
            "message": "결과 파일에서 취약점을 찾을 수 없습니다.",
            "result": None
        }), 404

    # 여기까지 왔다면 파일을 정상적으로 로드했다는 의미
    print(f"[DEBUG] 파싱 시작. 취약점 개수: {len(results)}")

    # target_fingerprint가 지정된 경우 해당 fingerprint의 취약점만 필터링
    if target_fingerprint:
        filtered_results = [r for r in results if r.get("extra", {}).get("fingerprint") == target_fingerprint]
        if not filtered_results:
            return jsonify({
                "status": 404,
                "message": f"지문 '{target_fingerprint}'에 대한 취약점을 찾을 수 없습니다.",
                "result": None
            }), 404
        match = filtered_results[0]
    else:
        match = results[0]  # fingerprint가 지정되지 않은 경우 첫 번째 취약점 사용

    file = match.get("path", "")
    start = match.get("start", {})
    end = match.get("end", {})
    check_id = match.get("check_id", "")
    message = match.get("extra", {}).get("message", "")
    severity = match.get("extra", {}).get("severity", "")
    code_snippet = match.get("lines", "").strip()
    metadata = match.get("extra", {}).get("metadata", {})

    # fingerprint를 사용하여 파일 찾기
    vulnerable_code = ""
    try:
        fingerprint = match.get("extra", {}).get("fingerprint")
        if fingerprint:
            # translated.json 파일 읽기
            translated_file = os.path.join(RESULT_DIR, f"{file_id}_translated.json")
            print(f"[DEBUG] 읽을 translated 파일: {translated_file}")
            
            if os.path.exists(translated_file):
                with open(translated_file, 'r', encoding='utf-8-sig') as f:
                    translated_data = json.load(f)

                # fingerprint에 해당하는 결과 찾기
                target_result = None
                for result in translated_data.get("results", []):
                    if result.get("extra", {}).get("fingerprint") == fingerprint:
                        target_result = result
                        break
                
                if target_result:
                    # uploads 디렉토리에서 실제 파일 읽기
                    uploads_dir = os.path.join("uploads", file_id)
                    source_file = os.path.join(uploads_dir, target_result.get("path", ""))
                    print(f"[DEBUG] 읽을 uploads 파일: {source_file}")
                    
                    if os.path.exists(source_file):
                        with open(source_file, 'r', encoding='utf-8-sig') as f:
                            vulnerable_code = f.read()
                        print(f"[DEBUG] 파일 읽기 성공")
                    else:
                        print(f"[DEBUG] uploads에서 파일을 찾을 수 없음: {source_file}")
                        vulnerable_code = code_snippet
                else:
                    print(f"[DEBUG] translated.json에서 fingerprint를 찾을 수 없음: {fingerprint}")
                    vulnerable_code = code_snippet
            else:
                print(f"[DEBUG] translated.json 파일을 찾을 수 없음: {translated_file}")
                vulnerable_code = code_snippet
        else:
            print("[DEBUG] fingerprint를 찾을 수 없음")
            vulnerable_code = code_snippet
    except Exception as e:
        print(f"[DEBUG] 원본 코드 읽기 실패: {str(e)}")
        vulnerable_code = code_snippet  # 실패시 code_snippet 사용

    references = metadata.get("references", [])
    rule_url = metadata.get("semgrep.dev.rule.url")
    if rule_url and rule_url not in references:
        references.append(rule_url)

    unique_id = f"{file}_{start.get('line', 0)}_{start.get('col', 0)}_{check_id}"

    # AI 리포트 정보 확인
    ai_report = False
    ai_report_contents = None
    if record and "ai_reports" in record:
        ai_report = True
        ai_report_contents = record.get("ai_reports", {})

    result = {
        "user_id": None,
        "id": unique_id,
        "file": file,
        "location": {
            "start": {
                "line": start.get("line"),
                "column": start.get("col")
            },
            "end": {
                "line": end.get("line"),
                "column": end.get("col")
            }
        },
        "type": check_id,
        "message": message,
        "severity": severity,
        "suggestion": message,
        "code_snippet": code_snippet,
        "code": vulnerable_code,  # uploads에서 읽은 소스 파일의 내용
        "metadata": {
            "cwe": metadata.get("cwe", []),
            "category": metadata.get("category", ""),
            "technology": metadata.get("technology", []),
            "subcategory": metadata.get("subcategory", []),
            "likelihood": metadata.get("likelihood", ""),
            "impact": metadata.get("impact", ""),
            "vulnerability_class": metadata.get("vulnerability_class", [])
        },
        "references": references,
        "ai_report": ai_report,
        "ai_report_contents": ai_report_contents
    }

    # DB에 상세 보고서 저장
    if record:
        save_detailed_report(file_id, result)

    return jsonify({
        "status": 200,
        "message": "성공",
        "result": result
    }), 200
