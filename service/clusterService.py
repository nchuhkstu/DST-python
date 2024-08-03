import os.path
import shutil
import time

from config import cluster_path


class ClusterService:
    def __init__(self):
        self.template_cluster_path = os.getcwd()
        self.cluster_path = cluster_path + "/DST"

    def get(self):
        if not os.path.exists(self.cluster_path):
            os.makedirs(self.cluster_path)
        clusters = []
        for item in os.listdir(self.cluster_path):
            clusters.append(item)
        return clusters

    def add(self):
        if not os.path.exists(self.cluster_path):
            os.makedirs(self.cluster_path)
        index = 0
        for item in os.listdir(self.cluster_path):
            if os.path.isdir(os.path.join(self.cluster_path, item)):
                index = int(item[-1])
        cluster_name = "Cluster_" + str(index + 1)
        new_cluster_path = os.path.join(self.cluster_path, cluster_name)
        shutil.copytree(self.template_cluster_path, new_cluster_path)
        os.utime(new_cluster_path, times=(time.time(), time.time()))

    def delete(self, cluster_name):
        shutil.rmtree(os.path.join(self.cluster_path, cluster_name))

    def upload(self, file):
        pass


clusterService = ClusterService()
clusterService.add()
