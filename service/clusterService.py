import os.path
import shutil
import time

from config import cluster_path


class ClusterService:
    def __init__(self):
        self.template_cluster_path = os.getcwd() + "/cluster/template"
        self.cluster_path = cluster_path + "/DST"

    def get(self):
        if not os.path.exists(self.cluster_path):
            os.makedirs(self.cluster_path)
        clusters = []
        cluster_names = sorted(os.listdir(self.cluster_path), key=len)
        for cluster_name in cluster_names:
            cluster = {"cluster_name": cluster_name}
            path = os.path.join(self.cluster_path, cluster_name)
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
                    if "cluster_name" in line:
                        cluster["server_name"] = line.split(" = ")[1].strip()
            master_port = None
            with open(os.path.join(path, "Master", "server.ini"), "r", encoding='utf-8') as file:
                for line in file:
                    if "server_port" in line:
                        master_port = line.split(" = ")[1].strip()
            with open(os.path.join(path, "Caves", "server.ini"), "r", encoding='utf-8') as file:
                for line in file:
                    if "server_port" in line and "master_server_port" not in line:
                        cluster["port"] = master_port + "," + line.split(" = ")[1].strip()
            clusters.append(cluster)
        return clusters

    def add(self):
        if not os.path.exists(self.cluster_path):
            os.makedirs(self.cluster_path)
        index = 0
        items = sorted(os.listdir(self.cluster_path), key=len)
        for item in items:
            print(item)
            for i in range(len(item)):
                if item[i] == "_":
                    index = int(item[i + 1:])
        cluster_name = "Cluster_" + str(index + 1)
        new_cluster_path = os.path.join(self.cluster_path, cluster_name)
        shutil.copytree(self.template_cluster_path, new_cluster_path)
        os.utime(new_cluster_path, times=(time.time(), time.time()))
        return {"cluster_name": cluster_name, "server_name": "默认初始的世界", "game_mode": "生存", "days": "0",
                "people_num": "0/8", "status": "停止", "port": "10999,10998"}

    def delete(self, cluster_name):
        shutil.rmtree(os.path.join(self.cluster_path, cluster_name))
        return "true"

    def upload(self, file):
        pass

