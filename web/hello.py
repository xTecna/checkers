import os
from flask import Flask, request, jsonify, send_from_directory
from app import ai

app = Flask(__name__, static_url_path="/static")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def route(path):
    return send_from_directory("static", path)

def convert(board, hop):
    flatten = []
    for row in board:
        flatten.extend(row)
    return tuple(flatten + [tuple(hop)] + [2])

@app.route("/next", methods = ["POST"])
def next_move():
    monteCarlo = ai.MonteCarlo(ai.Board())
    content = request.json

    monteCarlo.update(convert(content["board"], content["hop"]))
    action = monteCarlo.get_play()
    
    return jsonify({"move" : list(action)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)