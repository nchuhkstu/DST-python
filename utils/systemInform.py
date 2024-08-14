import ctypes
import datetime

import cpuinfo
import psutil
from utils.socketIO import socketIO


def system_information_static():
    info = cpuinfo.get_cpu_info()
    data = {
        "name": info["brand_raw"],
        'basic_frequency': info["hz_advertised_friendly"][:4] + info["hz_advertised_friendly"][-3:],
        "core_num": psutil.cpu_count(logical=False),
        "core_num_logical": psutil.cpu_count(logical=True),
        "l2_cache_size": str(info["l2_cache_size"] / 1024 / 1024) + "MB",
        "l3_cache_size": str(info["l3_cache_size"] / 1024 / 1024) + "MB",
        "cpu_virtual": "未启用"
    }
    if 'vmx' or 'svm' in info["flags"]:
        data['cpu_virtual'] = "已启用"
    return data


system_information = system_information_static()


def get_cpu_uptime():
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    days, remainder = divmod(uptime.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)}:{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"


lib = ctypes.CDLL('./Project1.dll')


class CpuData(ctypes.Structure):
    _fields_ = [
        ('usage', ctypes.POINTER(ctypes.c_double)),
        ('frequency', ctypes.c_double),
        ('process_count', ctypes.c_double),
        ('thread_count', ctypes.c_double),
        ('handle_count', ctypes.c_double)
    ]


class MemoryData(ctypes.Structure):
    _fields_ = [
        ('available', ctypes.c_double),
        ('available_2', ctypes.c_double),
        ('commited', ctypes.c_double),
        ('commited_percent', ctypes.c_double),
        ('pool_paged', ctypes.c_double),
        ('pool_not_paged', ctypes.c_double)
    ]


class Data(ctypes.Structure):
    _fields_ = [
        ('cpuData', CpuData),
        ('memoryData', MemoryData)
    ]


# 定义 getCurrentCpuUsage 函数
lib.getCurrentCpuUsage.argtypes = [ctypes.c_int]
lib.getCurrentCpuUsage.restype = Data
lib.cpuProcessUsage.argtypes = [ctypes.c_char_p]
lib.cpuProcessUsage.restype = ctypes.c_double


def system_information_running():
    num = system_information["core_num_logical"]
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
            }
        }

        for i in range(num + 1):  # 假设 num 为 5
            result["cpuData"]["usage"][i] = round(float(data.cpuData.usage[i]), 1)
        socketIO.emit('system_information', result)




