from PIL import Image
import numpy as np

# 生成一个示例的二维数组表示的数字矩阵
matrix = [
    [0, 255, 0, 255, 0],
    [255, 0, 255, 0, 255],
    [0, 255, 0, 255, 0],
    [255, 0, 255, 0, 255],
    [0, 255, 0, 255, 0]
]


# 定义 RGB 颜色映射函数
def map_value_to_color(value):
    if value == 0:
        return 255, 0, 0  # 红色
    elif value == 255:
        return 0, 255, 0  # 绿色
    else:
        return 0, 0, 255  # 蓝色


# 将二维数组转换为 NumPy 数组，并根据 RGB 颜色映射函数转换为 RGB 图像
data = np.array([[map_value_to_color(value) for value in row] for row in matrix], dtype=np.uint8)
img = Image.fromarray(data)

# 保存图像文件
img.save('rgb_matrix_image.png')

# 显示图像
img.show()
