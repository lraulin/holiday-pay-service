from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from datetime import datetime
import holiday_controller as hc

app: Flask = Flask(__name__)
CORS(app)


@app.route('/holiday', methods=['POST'])
def calculate_pay():
    body = request.json
    # Get date from query parameter
    holiday: datetime = datetime.strptime(body['date'], "%Y-%m-%d")
    # Get CSV from request body
    csv: str = body['csv']

    # Process data
    output = hc.process_csv(holiday, csv)
    response = jsonify(output)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run()
