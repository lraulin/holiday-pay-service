from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from datetime import datetime
import holiday_controller as hc

app: Flask = Flask(__name__)
CORS(app)

@app.route('/holiday', methods=['POST'])
def calculate_pay():
    body = request.json
    print(body)
    # Get date from query parameter
    holiday: datetime = datetime.strptime(body['date'], "%Y-%m-%d")
    # Get CSV from request body
    csv: str = body['csv']

    # Process data
    output = hc.process_csv(holiday, csv)

    return jsonify(output)


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    return response


if __name__ == '__main__':
    app.run()
