import os.path

import config


class SystemService:
    def __init__(self):
        self.cluster_path = config.cluster_path
        self.exe_path = config.exe_path
        self.config_path = os.getcwd()
        pass

    def get(self):
        return {"cluster_path": self.cluster_path, "exe_path": self.exe_path}

    def post(self, path_cluster, path_exe):
        self.cluster_path = path_cluster
        self.exe_path = path_exe
        with open(os.path.join(self.config_path, "config.py"), "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open(os.path.join(self.config_path, "config.py"), "w", encoding="utf-8") as file:
            for line in lines:
                if "cluster_path" in line:
                    file.write(f'cluster_path = "{self.cluster_path}"\n')
                elif "exe_path" in line:
                    file.write(f'exe_path = "{self.exe_path}"\n')
                else:
                    file.write(line)
        return "ok"
