from flask import Flask, request, jsonify, render_template
import numpy as np
import logging
import json
from pathlib import Path
import time

app = Flask(__name__)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
EVENT_HISTORY = None

def init_database():
    global EVENT_HISTORY
    EVENT_HISTORY = {"door_opened": np.array([]), "door_closed": np.array([]), "PIR": np.array([])}
# init_database()
@app.route('/upload', methods=['POST'])
def upload_json():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        data = json.load(file)
        for event, timestamps in data.items():
            if event in EVENT_HISTORY:
                EVENT_HISTORY[event] = np.hstack((EVENT_HISTORY[event], np.array(timestamps)))
        return jsonify({"success": "Valid JSON format"}), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/view')
def index():
    # table_data = [EVENT_HISTORY[key] for key in EVENT_HISTORY]
    table_data = [EVENT_HISTORY[key] for key in EVENT_HISTORY]
    shape = (len(EVENT_HISTORY), max([len(column) for column in table_data]))
    array_data = np.full(shape, None)
    for i in range(shape[0]):
        array_data[i, :len(table_data[i])] = np.array(table_data[i])
    headers = list(EVENT_HISTORY.keys())
    array_data = array_data.T
    # return render_template('C:\\Users\\vojte\\PycharmProjects\\SPD_TOM\\server\\view_template.html', headers=headers, table_data=table_data)
    return render_template('view_template.html', headers=headers, table_data=array_data)

@app.route('/reset')
def reset():
    init_database()
    return jsonify({"success": "database reset"}), 200

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
