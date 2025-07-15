from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

@app.route('/')
def index():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    return render_template('index.html', data=data)

@app.route('/api/data', methods=['POST'])
def api_data():
    data = request.get_json()
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify({"status": "success"})

@app.route('/api/latest')
def api_latest():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)