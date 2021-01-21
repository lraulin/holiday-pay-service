from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin
from datetime import datetime
from dateparser import parse
import holiday_controller as hc

app: Flask = Flask(__name__)


@app.route('/holiday', methods=['POST'])
@cross_origin()
def calculate_pay():
    body = request.json
    # Get date from request body
    holiday: datetime = parse(body['date'])
    # Get CSV from request body
    csv: str = body['csv']

    # Process data
    output = hc.process_csv(holiday, csv)
    response = jsonify(output)
    return response


if __name__ == '__main__':
    app.run()
