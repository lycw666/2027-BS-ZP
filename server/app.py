

import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template

app = Flask(__name__)

# 数据库固定放在项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "environment.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/latest")
def latest_data():
    conn = get_db()

    rows = conn.execute("""
        SELECT s.*
        FROM sensor_data s
        INNER JOIN (
            SELECT node_id, MAX(id) AS max_id
            FROM sensor_data
            GROUP BY node_id
        ) latest ON s.id = latest.max_id
        ORDER BY s.node_id
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/history")
def history_data():
    conn = get_db()

    rows = conn.execute("""
        SELECT node_id, timestamp, temperature, humidity, light
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in reversed(rows)])


@app.route("/api/statistics")
def statistics():
    conn = get_db()

    total = conn.execute("""
        SELECT COUNT(*) FROM sensor_data
    """).fetchone()[0]

    nodes = conn.execute("""
        SELECT node_id, COUNT(*) AS count
        FROM sensor_data
        GROUP BY node_id
    """).fetchall()

    conn.close()

    return jsonify({
        "total_records": total,
        "nodes": [dict(row) for row in nodes]
    })


if __name__ == "__main__":
    print("环境监测 Web 服务启动中...")
    print("浏览器访问：http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
