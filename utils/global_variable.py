import ctypes


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


class NetworkData(ctypes.Structure):
    _fields_ = [
        ('total', ctypes.c_double),
        ('sent', ctypes.c_double),
        ('receive', ctypes.c_double),
    ]


class Data(ctypes.Structure):
    _fields_ = [
        ('cpuData', CpuData),
        ('memoryData', MemoryData),
        ('networkData', NetworkData)
    ]


class ProcessData(ctypes.Structure):
    _fields_ = [
        ('cpu', ctypes.c_double),
        ('memory', ctypes.c_double),
    ]


server_dict = {}
system_info = {}
cluster_path, exe_path = None, None
lib = ctypes.CDLL('../_internal/system.dll')
# 定义 getCurrentCpuUsage 函数
lib.getCurrentCpuUsage.argtypes = [ctypes.c_int]
lib.getCurrentCpuUsage.restype = Data
lib.cpuProcessUsage.argtypes = [ctypes.c_char_p]
lib.cpuProcessUsage.restype = ProcessData
