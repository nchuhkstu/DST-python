import ctypes
import time

dll = ctypes.CDLL('./project1.dll')

# 设置返回值类型为 double
dll.getCurrentCpuUsage.restype = ctypes.c_double

while True:
    cpu_usage = dll.getCurrentCpuUsage("0")
    print(cpu_usage)
