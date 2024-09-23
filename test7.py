import time
import numpy as np

# 创建一个大的随机数组
large_array = np.random.rand(10**8)

# 未优化的累加和计算
def sum_array_unoptimized(arr):
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total

def sum_array_optimized(arr, block_size=1024):
    total = 0
    for start in range(0, len(arr), block_size):
        end = min(start + block_size, len(arr))
        for i in range(start, end):
            total += arr[i]
    return total

# 测量执行时间
start_time = time.time()
total_unoptimized = sum_array_optimized(large_array)
end_time = time.time()

print(f"未优化的总和: {total_unoptimized}")
print(f"执行时间: {end_time - start_time:.6f} 秒")
