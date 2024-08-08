import os.path


class SystemService:
    def __init__(self):
        with open("config.ini", "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                if "cluster_path" in line:
                    self.cluster_path = line.split(" = ")[1].strip()
                if "exe_path" in line:
                    self.exe_path = line.split(" = ")[1].strip()
        self.config_path = os.getcwd()
        pass

    def get(self):
        return {"cluster_path": self.cluster_path, "exe_path": self.exe_path}

    def post(self, path_cluster, path_exe):
        self.cluster_path = path_cluster
        self.exe_path = path_exe
        with open("config.ini", "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open("config.ini", "w", encoding="utf-8") as file:
            for line in lines:
                if "cluster_path" in line:
                    file.write(f'cluster_path = {self.cluster_path}\n')
                elif "exe_path" in line:
                    file.write(f'exe_path = {self.exe_path}\n')
                else:
                    file.write(line)
        return {"status": "ok", "message": "保存成功"}
