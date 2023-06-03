#!/usr/bin/env python3

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/status', methods=['GET', 'POST'])
def api_status():
    if request.method == 'GET':
        return jsonify({"status": "OK"}), 200
    elif request.method == 'POST':
        status = request.json["status"]
        print(status)
        return jsonify({"status": status}), 201