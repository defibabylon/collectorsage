#!/usr/bin/env python3
"""
Minimal Flask test to check if the server is working
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Hello from minimal Flask app!'})

@app.route('/test')
def test():
    return jsonify({'status': 'success', 'message': 'Test endpoint working'})

if __name__ == '__main__':
    print("Starting minimal Flask app on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
