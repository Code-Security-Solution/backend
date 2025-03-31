from flask import Flask
from handle_scan_request import scan_code
from handle_get_result import get_scan_result
from handle_get_summary import get_summary_report

app = Flask(__name__)

app.add_url_rule('/scan', view_func=scan_code, methods=['POST'])
app.add_url_rule('/scan-result/<file_id>', view_func=get_scan_result, methods=['GET'])
app.add_url_rule('/summary-report/<file_id>', view_func=get_summary_report, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
