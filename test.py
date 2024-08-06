import time
import ctypes
from ctypes import wintypes

def get_current_cpu_speed():
    # Open PDH
    query = wintypes.HANDLE()
    status = ctypes.windll.pdh.PdhOpenQuery(None, None, ctypes.byref(query))
    if status != 0:  # ERROR_SUCCESS
        return -1

    cpu_performance = wintypes.HANDLE()
    cpu_basic_speed = wintypes.HANDLE()

    # Add CPU current performance counter
    status = ctypes.windll.pdh.PdhAddCounter(query, "\\Processor Information(_Total)\\% Processor Performance", None, ctypes.byref(cpu_performance))
    if status != 0:  # ERROR_SUCCESS
        return -1

    # Add CPU base frequency counter
    status = ctypes.windll.pdh.PdhAddCounter(query, "\\Processor Information(_Total)\\Processor Frequency", None, ctypes.byref(cpu_basic_speed))
    if status != 0:  # ERROR_SUCCESS
        return -1

    # Collect data
    ctypes.windll.pdh.PdhCollectQueryData(query)
    time.sleep(1)
    ctypes.windll.pdh.PdhCollectQueryData(query)

    pdh_value = wintypes.PDH_FMT_COUNTERVALUE()
    dw_value = wintypes.DWORD()

    status = ctypes.windll.pdh.PdhGetFormattedCounterValue(cpu_performance, 0x00000002, ctypes.byref(dw_value), ctypes.byref(pdh_value))  # PDH_FMT_DOUBLE
    if status != 0:  # ERROR_SUCCESS
        return -1
    cpu_performance_value = pdh_value.doubleValue / 100.0

    status = ctypes.windll.pdh.PdhGetFormattedCounterValue(cpu_basic_speed, 0x00000002, ctypes.byref(dw_value), ctypes.byref(pdh_value))  # PDH_FMT_DOUBLE
    if status != 0:  # ERROR_SUCCESS
        return -1
    basic_speed_value = pdh_value.doubleValue

    # Close PDH
    ctypes.windll.pdh.PdhCloseQuery(query)

    return cpu_performance_value * basic_speed_value

if __name__ == "__main__":
    while True:
        print(get_current_cpu_speed())

