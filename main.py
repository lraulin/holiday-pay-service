from flask import Flask, request, jsonify
from datetime import datetime
import holiday_controller as hc

app: Flask = Flask(__name__)

@app.route('/holiday', methods=['POST'])
def calculate_pay():
    # Get date from query parameter
    holiday: datetime = datetime.strptime(request.args['holiday'], "%Y-%m-%d")
    # Get CSV from request body
    csv: bytes = request.get_data()

    # Process data
    output = hc.process_csv(holiday, csv)

    return output



if __name__ == '__main__':
    app.run()
