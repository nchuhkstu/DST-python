import os


def read_config(work_path):
    steamCMD_path, cluster_path, exe_path = None, None, None
    with open(os.path.join(work_path, "config.ini"), "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            if "steamCMD_path" in line:
                steamCMD_path = line.split("=")[1].strip()
            if "cluster_path" in line:
                cluster_path = line.split(" = ")[1].strip()
            if "exe_path" in line:
                exe_path = line.split(" = ")[1].strip()
            if "port" in line:
                port = line.split(" = ")[1].strip()
    return steamCMD_path, cluster_path, exe_path, port


g_variable = {
    'steamCMD_path': read_config(os.getcwd())[0],
    'cluster_path': read_config(os.getcwd())[1],
    'exe_path': read_config(os.getcwd())[2],
    'port': int(read_config(os.getcwd())[3]),
}
