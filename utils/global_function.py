import os
import time
import uuid

import requests

from utils.configLoader import g_variable
from lupa import LuaRuntime
import urllib.request
import json
from utils.dataBase import conn
from utils.global_variable import user, cache

lua = LuaRuntime(unpack_returned_tuples=True)


def update_user_data(cluster_name):
    if cluster_name not in user:
        user[cluster_name] = {}
    folder = os.path.join(g_variable["cluster_path"], "DST", cluster_name, "Master", "save", "session")
    for root, dirs, files in os.walk(folder):
        if root.count(os.sep) == folder.count(os.sep) + 2:
            for file in files:
                if file.startswith("000") and not file.endswith(".meta"):
                    user_folder = os.path.basename(root)[:-1]
                    if user_folder not in user[cluster_name]:
                        user[cluster_name][user_folder] = {}
                    # print(os.path.join(root, file))
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line in lines:
                            if "return" in line:
                                break
                    start_index = line.find('n {') + 2
                    brace_count = 0
                    end_index = 0
                    for i in range(start_index, len(line)):
                        if line[i] == '{':
                            brace_count += 1
                        elif line[i] == '}':
                            brace_count -= 1
                        if brace_count == 0:
                            end_index = i + 1
                            break
                    raw_user = line[start_index:end_index]
                    # print(raw_user)
                    lua_table = lua.eval(raw_user)

                    cursor = conn.cursor()
                    query = """SELECT name FROM users WHERE cluster_name = ? AND userid = ?"""
                    values = (cluster_name, user_folder)
                    cursor.execute(query, values)
                    name = cursor.fetchone()[0]
                    cursor.close()
                    if cluster_name not in cache:
                        cache[cluster_name] = {}
                    user[cluster_name][user_folder] = {
                        "temperature": int(lua_table.data.temperature.current),
                        "survivalTime": int(lua_table.data.age.age),
                        # "hunger": int(lua_table.data.hunger.hunger),
                        "sanity": int(lua_table.data.sanity.current),
                        "health": int(lua_table.data.health.health),
                        "role": lua_table.prefab,
                        "name": name,
                        "online": "online" if name in cache[cluster_name] else user[cluster_name][user_folder].get("online", "outline"),
                        "player": "玩家"
                    }
    path = os.path.join(g_variable["cluster_path"] + "/DST", cluster_name)
    with open(os.path.join(path, "adminlist.txt"), "r", encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            userid = line.strip()
            if userid in user[cluster_name]:
                user[cluster_name][userid]["player"] = "管理员"
    with open(os.path.join(path, "cluster_token.txt"), "r", encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            start_index = line.find('KU_')
            userid = line[start_index:start_index + 11]
            if userid in user[cluster_name]:
                user[cluster_name][userid]["player"] = "服主"


def public_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["ip"]
    except Exception as e:
        print(f"Error occurred: {e}")
        return ""


def send_remote_start(cluster_name):
    key = str(uuid.uuid4())
    with open(os.path.join(g_variable["cluster_path"], "DST", cluster_name, "cluster.ini"), 'r',
              encoding='utf-8') as file:
        for line in file:
            if "cluster_name" in line:
                room_name = line.split(" = ")[1].strip()
                break
    while True:

        data = {
            "key": key,
            "ip": public_ip(),
            "room_name": room_name,
            "time": int(time.time())
        }
        print(data)
        requests.post("123123", json=data)
        time.sleep(1)
