import json
import time
from PIL import Image

from utils.dataBase import conn

# 预加载所有可能使用的图像
image_paths = {
    2: Image.open("C:/Users/qhl666/Desktop/images/mini_cobblestone_noise.png"),
    3: Image.open("C:/Users/qhl666/Desktop/images/mini_rocky_noise.png"),
    4: Image.open("C:/Users/qhl666/Desktop/images/mini_dirt_noise.png"),
    5: Image.open("C:/Users/qhl666/Desktop/images/mini_grass2_noise.png"),
    6: Image.open("C:/Users/qhl666/Desktop/images/mini_grass_noise.png"),
    7: Image.open("C:/Users/qhl666/Desktop/images/mini_forest_noise.png"),
    8: Image.open("C:/Users/qhl666/Desktop/images/mini_marsh_noise.png"),
    9: Image.open("C:/Users/qhl666/Desktop/images/web_noise.png").resize((256, 256)),

    10: Image.open("C:/Users/qhl666/Desktop/images/mini_woodfloor_noise.png"),
    11: Image.open("C:/Users/qhl666/Desktop/images/mini_carpet_noise.png"),
    12: Image.open("C:/Users/qhl666/Desktop/images/mini_checker_noise.png"),
    13: Image.open("C:/Users/qhl666/Desktop/images/mini_cave_noise.png"),

    30: Image.open("C:/Users/qhl666/Desktop/images/mini_deciduous_noise.png"),
    31: Image.open("C:/Users/qhl666/Desktop/images/mini_desert_dirt_noise.png"),
    34: Image.open("C:/Users/qhl666/Desktop/images/lavaarena_trim_mini.png"),
    42: Image.open("C:/Users/qhl666/Desktop/images/mini_pebblebeach.png"),
    43: Image.open("C:/Users/qhl666/Desktop/images/mini_meteor.png"),
    44: Image.open("C:/Users/qhl666/Desktop/images/ground_noise_shellbeach.png").resize((256, 256)),
    201: Image.open("C:/Users/qhl666/Desktop/images/mini_water_shallow.png"),
    202 :Image.new('RGB', (256, 256), (23,  51,  62)),
    203: Image.new('RGB', (256, 256), (14, 34, 61)),
    204: Image.new('RGB', (256, 256), (19, 20, 40)),
    205: Image.new('RGB', (256, 256), (40, 87, 93)),
    206: Image.open("C:/Users/qhl666/Desktop/images/mini_water_coral.png"),
    207: Image.new('RGB', (256, 256), (8,   8,   14)),
    208: Image.new('RGB', (256, 256), (40, 87, 93)),
    257: Image.open("C:/Users/qhl666/Desktop/images/ground_noise_monkeyisland.png").resize((256, 256)),
    260: Image.open("C:/Users/qhl666/Desktop/images/mini_woodfloor_noise.png"),
    265: Image.open("C:/Users/qhl666/Desktop/images/noise_mosaictiles_grey.png"),
    268: Image.open("C:/Users/qhl666/Desktop/images/mini_carpet2_noise.png"),
}


def get_map(cluster_name):

    cursor = conn.cursor()
    query = """SELECT * FROM maps WHERE cluster_name = ?"""
    values = (cluster_name,)
    cursor.execute(query, values)
    points = cursor.fetchone()
    if not points:
        return {"status": "error", "message": "地图尚未生成"}
    conn.commit()
    cursor.close()

    points = json.loads(points[1])
    per_num = 28
    small_image_size = 9

    big_image = Image.new('RGB', (3840, 3840))

    points_length = len(points)
    dict = {}
    for i in range(len(points)):
        for j in range(len(points[i])):
            digit = int(points[i][j])
            if digit in image_paths:
                small_image = image_paths[digit]
                left = (i % per_num) * small_image_size
                upper = (j % per_num) * small_image_size
                big_image.paste(small_image.crop((left, upper, left + small_image_size, upper + small_image_size)),
                                (j * small_image_size, i * small_image_size))
            else:
                if digit not in dict:
                    dict[digit] = 0
                else:
                    dict[digit] += 1
    print(dict)
    big_image.show()

start = time.time()
get_map('Cluster_2')
end = time.time()
print(end - start)

