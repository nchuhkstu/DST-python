import io
import json
import os.path
import shutil
import time

import numpy as np
from PIL import Image, ImageFilter
from flask import send_file

from utils.configLoader import g_variable
from utils.global_function import generate_map
from utils.global_variable import server_dict, user
from utils.dataBase import conn


class ClusterService:
    def __init__(self):
        # self.template_cluster_path = os.getcwd() + "/_internal/cluster/template"
        self.template_cluster_path = os.getcwd() + "/cluster/template"

    @staticmethod
    def get():
        if not os.path.exists(g_variable["cluster_path"]):
            return "false"
        clusters = []
        cluster_names = sorted(os.listdir(g_variable["cluster_path"]), key=len)
        for cluster_name in cluster_names:
            cluster = {"cluster_name": cluster_name, "current_players": "0", "status": "未启动", "days": "0"}
            path = os.path.join(g_variable["cluster_path"], cluster_name)
            with open(os.path.join(path, "cluster.ini"), "r", encoding='utf-8') as file:
                for line in file:
                    if "game_mode" in line:
                        parts = line.split(" = ")
                        if parts[1].strip() == "endless":
                            cluster["game_mode"] = "无尽"
                        elif parts[1].strip() == "survival":
                            cluster["game_mode"] = "生存"
                        elif parts[1].strip() == "wilderness":
                            cluster["game_mode"] = "荒野"
                    elif "cluster_name" in line:
                        cluster["server_name"] = line.split(" = ")[1].strip()
                    elif "max_players" in line:
                        cluster["max_players"] = line.split(" = ")[1].strip()
            master_port, communicate_port = None, None
            with open(os.path.join(path, "cluster.ini"), "r", encoding='utf-8') as file:
                for line in file:
                    if "master_port" in line:
                        communicate_port = line.split(" = ")[1].strip()
            with open(os.path.join(path, "Master", "server.ini"), "r", encoding='utf-8') as file:
                for line in file:
                    if "server_port" in line:
                        master_port = line.split(" = ")[1].strip()
            with open(os.path.join(path, "Caves", "server.ini"), "r", encoding='utf-8') as file:
                for line in file:
                    if "server_port" in line and "master_server_port" not in line:
                        cluster["port"] = master_port + "," + line.split(" = ")[1].strip() + "," + communicate_port
            if cluster_name in server_dict:
                cluster["current_players"] = server_dict[cluster_name]["current_players"]
                cluster["status"] = server_dict[cluster_name]["status"]
            clusters.append(cluster)
        return clusters

    @staticmethod
    def get_map(cluster_name):
        cursor = conn.cursor()
        query = """SELECT * FROM maps WHERE cluster_name = ?"""
        values = (cluster_name,)
        cursor.execute(query, values)
        points = cursor.fetchone()
        if not points:
            return {"status": "error", "message": "地图尚未生成"}
        conn.commit()
        cursor.close()
        data = np.array(json.loads(points[1]), dtype=np.uint8)
        color_map = {
            3: (77, 64, 43),
            4: (117, 107, 87),
            5: (88, 67, 35),
            6: (60, 83, 51),
            7: (46, 53, 24),
            8: (46, 52, 82),
            30: (68, 52, 35),
            31: (115, 93, 49),
            34: (74, 67, 44),
            42: (74, 67, 44),
            43: (148, 209, 214),
            44: (75, 66, 44),
            201: (23, 51, 62),
            202: (23, 51, 62),
            203: (14, 34, 61),
            204: (19, 20, 40),
            205: (40, 87, 93),
            207: (8, 8, 14),
            208: (40, 87, 93),
        }
        colored_data = np.zeros((data.shape[0], data.shape[1], 3), dtype=np.uint8)
        for value, color in color_map.items():
            colored_data[data == value] = color
        img = Image.fromarray(colored_data)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return send_file(img_bytes, mimetype='image/png')

    def refresh_map(self, cluster_name):
        if cluster_name not in server_dict:
            return {"status": "error", "message": "服务器尚未启动，无法刷新地图"}
        generate_map(cluster_name)
        return self.get_map(cluster_name)

    @staticmethod
    def get_room(cluster_name):
        room = {"cluster_index": cluster_name}
        path = os.path.join(g_variable["cluster_path"], cluster_name)
        with open(os.path.join(path, "cluster.ini"), "r", encoding='utf-8') as file:
            for line in file:
                if "cluster_name" in line:
                    room["cluster_name"] = line.split(" = ")[1].strip()
                elif "cluster_description" in line:
                    room["cluster_description"] = line.split(" = ")[1].strip()
                elif "game_mode" in line:
                    room["game_mode"] = line.split(" = ")[1].strip()
                elif "max_players" in line:
                    room["max_players"] = line.split(" = ")[1].strip()
                elif "max_snapshots" in line:
                    room["max_snapshots"] = line.split(" = ")[1].strip()
                elif "cluster_password" in line:
                    room["cluster_password"] = line.split(" = ")[1].strip()
                elif "pvp" in line:
                    room["pvp"] = line.split(" = ")[1].strip()
                elif "pause_when_empty" in line:
                    room["pause_when_empty"] = line.split(" = ")[1].strip()
                elif "vote_enabled" in line:
                    room["vote_enabled"] = line.split(" = ")[1].strip()
                elif "vote_kick_enabled" in line:
                    room["vote_kick_enabled"] = line.split(" = ")[1].strip()
                elif "master_port" in line:
                    room["master_port"] = line.split(" = ")[1].strip()

        with open(os.path.join(path, "Master", "server.ini"), "r", encoding='utf-8') as file:
            for line in file:
                if "server_port" in line:
                    room["master_server_port"] = line.split(" = ")[1].strip()

        with open(os.path.join(path, "Caves", "server.ini"), "r", encoding='utf-8') as file:
            for line in file:
                if "server_port" in line and "master_server_port" not in line:
                    room["caves_server_port"] = line.split(" = ")[1].strip()
        return room

    @staticmethod
    def set_room(cluster):
        convert_true_to_string(cluster)
        path = os.path.join(g_variable["cluster_path"], cluster["cluster_index"])
        with open(os.path.join(path, "cluster.ini"), "r", encoding='utf-8') as file:
            lines = file.readlines()

        with open(os.path.join(path, "cluster.ini"), "w", encoding='utf-8') as file:
            for line in lines:
                if "cluster_name" in line:
                    file.write(f'cluster_name = {cluster["cluster_name"]}\n')
                elif "cluster_description" in line:
                    file.write(f'cluster_description = {cluster["cluster_description"]}\n')
                elif "game_mode" in line:
                    file.write(f'game_mode = {cluster["game_mode"]}\n')
                elif "max_players" in line:
                    file.write(f'max_players = {cluster["max_players"]}\n')
                elif "max_snapshots" in line:
                    file.write(f'max_snapshots = {cluster["max_snapshots"]}\n')
                elif "cluster_password" in line:
                    file.write(f'cluster_password = {cluster["cluster_password"]}\n')
                elif "pvp" in line:
                    file.write(f'pvp = {cluster["pvp"]}\n')
                elif "pause_when_empty" in line:
                    file.write(f'pause_when_empty = {cluster["pause_when_empty"]}\n')
                elif "vote_enabled" in line:
                    file.write(f'vote_enabled = {cluster["vote_enabled"]}\n')
                elif "vote_kick_enabled" in line:
                    file.write(f'vote_kick_enabled = {cluster["vote_kick_enabled"]}\n')
                elif "master_port" in line:
                    file.write(f'master_port = {cluster["master_port"]}\n')
                else:
                    file.write(line)

        with open(os.path.join(path, "Master", "server.ini"), "r", encoding='utf-8') as file:
            lines = file.readlines()
        with open(os.path.join(path, "Master", "server.ini"), "w", encoding='utf-8') as file:
            for line in lines:
                if "server_port" in line:
                    file.write(f'server_port = {cluster["master_server_port"]}\n')
                else:
                    file.write(line)

        with open(os.path.join(path, "Caves", "server.ini"), "r", encoding='utf-8') as file:
            lines = file.readlines()
        with open(os.path.join(path, "Caves", "server.ini"), "w", encoding='utf-8') as file:
            for line in lines:
                if "server_port" in line and "master_server_port" not in line:
                    file.write(f'server_port = {cluster["caves_server_port"]}\n')
                else:
                    file.write(line)
        return {"status": "ok", "message": "保存成功"}

    @staticmethod
    def get_log(cluster_name):
        path = os.path.join(g_variable["cluster_path"], cluster_name, "Master", "server_log.txt")
        if not os.path.exists(path):
            return {"status": "error", "message": "日志不存在"}
        log_list = []
        with open(path, "r", encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if ']:' in line and 'map:' not in line:
                    log_list.append({
                        "cluster_name": cluster_name,
                        "time": line.strip().split("]:")[0][1:],
                        "message": line.strip().split("]:")[1]
                    })
        return log_list

    def add(self):
        if not os.path.exists(g_variable["cluster_path"]):
            os.makedirs(g_variable["cluster_path"])
        index = 0
        items = sorted(os.listdir(g_variable["cluster_path"]), key=len)
        for item in items:
            for i in range(len(item)):
                if item[i] == "_":
                    index = int(item[i + 1:])
        cluster_name = "Cluster_" + str(index + 1)
        new_cluster_path = os.path.join(g_variable["cluster_path"], cluster_name)
        shutil.copytree(self.template_cluster_path, new_cluster_path)
        os.utime(new_cluster_path, times=(time.time(), time.time()))
        return {"status": "ok",
                "message": {"cluster_name": cluster_name, "server_name": "默认初始的世界", "game_mode": "生存",
                            "days": "0",
                            "max_players": "8", "current_players": "0", "status": "未启动", "port": "10999,10998"}
                }

    @staticmethod
    def delete(cluster_name):
        if cluster_name in server_dict:
            return {"status": "error", "message": "存档正在运行中"}
        cursor = conn.cursor()
        query = """ DELETE FROM users WHERE cluster_name = ? """
        values = (cluster_name,)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        cursor = conn.cursor()
        query = """ DELETE FROM maps WHERE cluster_name = ? """
        values = (cluster_name,)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        cursor = conn.cursor()
        query = """ DELETE FROM chat WHERE cluster_name = ? """
        values = (cluster_name,)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        shutil.rmtree(os.path.join(g_variable["cluster_path"], cluster_name))
        if cluster_name in user:
            del user[cluster_name]
        return {"status": "ok", "message": "存档已删除"}

    def upload(self, file):
        pass


def convert_true_to_string(d):
    for key, value in d.items():
        if isinstance(value, dict):
            convert_true_to_string(value)
        elif value is True:
            d[key] = "true"
        elif value is False:
            d[key] = "false"


def map_value_to_color(value):
    if value == 201:
        return 23, 51, 62, 102
    elif value == 202:
        return 23, 51, 62, 102
    elif value == 203:
        return 14, 34, 61, 204
    elif value == 204:
        return 19, 20, 40, 230
    elif value == 205:
        return 40, 87, 93, 51
    elif value == 207:
        return 8, 8, 14, 51
    else:
        return 0, 0, 0  # 蓝色
