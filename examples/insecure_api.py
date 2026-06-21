from flask import Flask, request, jsonify
import pickle
import subprocess
import yaml

app = Flask(__name__)

SECRET_KEY = "supersecretkey123"

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_data()
    obj = pickle.loads(data)
    return jsonify(obj)

@app.route("/run")
def run():
    cmd = request.args.get("cmd")
    output = subprocess.check_output(cmd, shell=True)
    return output

@app.route("/config")
def load_config():
    raw = request.args.get("yml")
    config = yaml.load(raw)
    return jsonify(config)

@app.route("/user/<user_id>")
def get_user(user_id):
    import sqlite3
    conn = sqlite3.connect("app.db")
    result = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return jsonify(result.fetchall())

if __name__ == "__main__":
    app.run(debug=True)
