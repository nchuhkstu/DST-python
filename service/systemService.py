import datetime
import os.path
import threading
import psutil
import requests
import wmi
from utils.configLoader import g_variable
from utils.global_variable import work_path, lib
from utils.socketIO import socketIO


class SystemService:
    def __init__(self):
        self.system_information = system_information_static()
        threading.Thread(target=self.system_information_running, args=()).start()

    def get(self):
        return {"steamCMD_path": g_variable["steamCMD_path"], "cluster_path": g_variable["cluster_path"],
                "exe_path": g_variable["exe_path"]}

    def post(self, steamCMD_path, path_cluster, path_exe):
        g_variable["steamCMD_path"] = steamCMD_path
        g_variable["cluster_path"] = path_cluster
        g_variable["exe_path"] = path_exe
        os.chdir(work_path)
        with open("config.ini", "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open("config.ini", "w", encoding="utf-8") as file:
            for line in lines:
                if "steamCMD_path" in line:
                    file.write(f'steamCMD_path = {g_variable["steamCMD_path"]}\n')
                elif "cluster_path" in line:
                    file.write(f'cluster_path = {g_variable["cluster_path"]}\n')
                elif "exe_path" in line:
                    file.write(f'exe_path = {g_variable["exe_path"]}\n')
                else:
                    file.write(line)
        return {"status": "ok", "message": "保存成功"}

    def get_system_info(self):
        return self.system_information

    def system_information_running(self):
        num = self.system_information["core_num_logical"]
        while True:
            data = lib.getCurrentCpuUsage(num)
            result = {
                "cpuData": {
                    "frequency": round(float(data.cpuData.frequency) / 1000, 2),
                    "process_count": data.cpuData.process_count,
                    "thread_count": data.cpuData.thread_count,
                    "handle_count": data.cpuData.handle_count,
                    "usage": {},
                    "running_time": get_cpu_uptime()
                },
                "memoryData": {
                    "available": data.memoryData.available,
                    "available_2": data.memoryData.available_2,
                    "total": psutil.virtual_memory().total / 1024 / 1024,
                    "commited": data.memoryData.commited,
                    "commited_percent": data.memoryData.commited_percent,
                    "pool_paged": data.memoryData.pool_paged,
                    "pool_not_paged": data.memoryData.pool_not_paged
                },
                "networkData": {
                    "total": formatted(data.networkData.total),
                    "sent": formatted(data.networkData.sent),
                    "receive": formatted(data.networkData.receive)
                }
            }

            for i in range(num + 1):  # 假设 num 为 5
                result["cpuData"]["usage"][i] = round(float(data.cpuData.usage[i]), 1)
            socketIO.emit('system_information', result)

    def downloading_steamCMD(self):
        if not os.path.exists(g_variable["steamCMD_path"]):
            return {"status": "ok", "message": "该路径不存在，下载错误"}
        if os.path.isfile(os.path.join(g_variable["steamCMD_path"], "steamcmd.exe")):
            return {"status": "ok", "message": "steamCMD已存于在该路径，请勿重复下载"}
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/58.0.3029.110 Safari/537.3',
                'Accept-Language': 'en-ZH,en;q=0.5',
            }
            response = requests.get("https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip", headers=headers,
                                    stream=True)
            response.raise_for_status()
            with open(g_variable["steamCMD_path"], 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return {"status": "ok", "message": "steamCMD已成功下载至 " + g_variable["steamCMD_path"]}
        except Exception as e:
            print(e)
            return {"status": "ok", "message": "下载失败错误为:" + str(e)}

    def update_game(self):
        pass


def get_cpu_uptime():
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    days, remainder = divmod(uptime.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)}:{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"


def system_information_static():
    info = wmi.WMI().Win32_Processor()
    data = {
        "name": info[0].Name,
        'basic_frequency': str(round(info[0].MaxClockSpeed / 1000, 2)) + 'GHZ',
        "core_num": psutil.cpu_count(logical=False),
        "core_num_logical": psutil.cpu_count(logical=True),
        "l2_cache_size": str(info[0].L2CacheSize / 1024) + "MB",
        "l3_cache_size": str(info[0].L3CacheSize / 1024) + "MB",
        "cpu_virtual": "已启用" if info[0].VirtualizationFirmwareEnabled else "否"
    }
    return data


def formatted(byte):
    if byte < 8 * 1024:
        return "{:.2f} B".format(byte / 8)
    if byte < 8 * 1024 * 1024:
        return "{:.2f} KB".format(byte / 8 / 1024)
    if byte < 8 * 1024 * 1024 * 1024:
        return "{:.2f} MB".format(byte / 8 / 1024 / 1024)
    if byte < 8 * 1024 * 1024 * 1024:
        return "{:.2f} GB".format(byte / 8 / 1024 / 1024 / 1024)
    if byte < 8 * 1024 * 1024 * 1024 * 1024:
        return "{:.2f} TB".format(byte / 8 / 1024 / 1024 / 1024 / 1024)
