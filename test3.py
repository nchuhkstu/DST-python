import threading
import time
from datetime import datetime
from flask_cors import CORS
import mysql.connector
from flask import Flask, request
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)
socketIO = SocketIO(cors_allowed_origins='*')
socketIO.init_app(app)
servers = {}
connection = mysql.connector.connect(
    host='8.138.88.84',         # 远程主机地址
    user='server',              # 数据库用户名
    password='Aa13657998660',   # 数据库密码
    database='server'           # 数据库名称
)


@app.route('/start', methods=['POST'])
def start():
    ip = request.remote_addr
    data = request.get_json()
    if data['key'] not in servers:
        servers[data['key']] = {"ip": ip, "room_name": data['room_name'], "start_time": data['time'],
                                "time": data['time'], "version": data['version']}
    else:
        servers[data['key']]["time"] = data["time"]
    return ""


@app.route('/running', methods=['GET'])
def get_running_server():
    return servers


@app.route('/stopped/<size>/<page>', methods=['GET'])
def get_stopped_server(size, page):
    cursor = connection.cursor()
    query = f"SELECT * FROM server LIMIT {int(size)} OFFSET {(int(page) - 1) * int(size)}"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results


def clean():
    while True:
        for server_key, server_info in servers.copy().items():
            if time.time() - server_info["time"] >= 10:
                cursor = connection.cursor()
                query = """INSERT INTO server (uuid, ip, room_name, start_time, end_time, view_version)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
                record = (server_key, server_info["ip"], server_info["room_name"], datetime.fromtimestamp(server_info["start_time"]).strftime('%Y-%m-%d %H:%M:%S'),
                          datetime.fromtimestamp(server_info["time"]).strftime('%Y-%m-%d %H:%M:%S'), server_info["version"])
                cursor.execute(query, record)
                connection.commit()
                cursor.close()
                del servers[server_key]
        time.sleep(1)


if __name__ == '__main__':
    threading.Thread(target=clean, daemon=True).start()
    socketIO.run(app, host='0.0.0.0', port=10000, allow_unsafe_werkzeug=True)
