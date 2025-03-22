from flask import Flask
from handle_scan_request import scan_code
from handle_get_result import get_scan_result

app = Flask(__name__)

app.add_url_rule('/scan', view_func=scan_code, methods=['POST'])
app.add_url_rule('/scan-result/<file_id>', view_func=get_scan_result, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
