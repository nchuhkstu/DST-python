import os.path
import shutil
import time

from controller.serverController import serverService
from controller.systemController import systemService


class ClusterService:
    def __init__(self):
        self.template_cluster_path = os.getcwd() + "/cluster/template"

    @staticmethod
    def get():
        if not os.path.exists(systemService.cluster_path + "/DST"):
            os.makedirs(systemService.cluster_path + "/DST")
        clusters = []
        cluster_names = sorted(os.listdir(systemService.cluster_path + "/DST"), key=len)
        for cluster_name in cluster_names:
            cluster = {"cluster_name": cluster_name, "current_players": "0", "status": "未启动", "days": "0"}
            path = os.path.join(systemService.cluster_path + "/DST", cluster_name)
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
            master_port = None
            with open(os.path.join(path, "Master", "server.ini"), "r", encoding='utf-8') as file:
                for line in file:
                    if "server_port" in line:
                        master_port = line.split(" = ")[1].strip()
            with open(os.path.join(path, "Caves", "server.ini"), "r", encoding='utf-8') as file:
                for line in file:
                    if "server_port" in line and "master_server_port" not in line:
                        cluster["port"] = master_port + "," + line.split(" = ")[1].strip()
            if cluster_name in serverService.server_dict:
                cluster["current_players"] = serverService.server_dict[cluster_name]["current_players"]
                cluster["status"] = serverService.server_dict[cluster_name]["status"]
            clusters.append(cluster)
        return clusters

    def add(self):
        if not os.path.exists(systemService.cluster_path + "/DST"):
            os.makedirs(systemService.cluster_path + "/DST")
        index = 0
        items = sorted(os.listdir(systemService.cluster_path + "/DST"), key=len)
        for item in items:
            print(item)
            for i in range(len(item)):
                if item[i] == "_":
                    index = int(item[i + 1:])
        cluster_name = "Cluster_" + str(index + 1)
        new_cluster_path = os.path.join(systemService.cluster_path + "/DST", cluster_name)
        shutil.copytree(self.template_cluster_path, new_cluster_path)
        os.utime(new_cluster_path, times=(time.time(), time.time()))
        return {"cluster_name": cluster_name, "server_name": "默认初始的世界", "game_mode": "生存", "days": "0",
                "max_players": "8", "current_players": "0", "status": "未启动", "port": "10999,10998"}

    @staticmethod
    def delete(cluster_name):
        shutil.rmtree(os.path.join(systemService.cluster_path + "/DST", cluster_name))
        return "true"

    def upload(self, file):
        pass

