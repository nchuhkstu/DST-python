import json
import time
from PIL import Image

from utils.dataBase import conn

image_paths = {
    2: Image.open("./images/mini_cobblestone_noise.png"),
    3: Image.open("./images/mini_rocky_noise.png"),
    4: Image.open("./images/mini_dirt_noise.png"),
    5: Image.open("./images/mini_grass2_noise.png"),
    6: Image.open("./images/mini_grass_noise.png"),
    7: Image.open("./images/mini_forest_noise.png"),
    8: Image.open("./images/mini_marsh_noise.png"),
    9: Image.open("./images/web_noise.png").resize((256, 256)),
    10: Image.open("./images/mini_woodfloor_noise.png"),
    11: Image.open("./images/mini_carpet_noise.png"),
    12: Image.open("./images/mini_checker_noise.png"),
    13: Image.open("./images/mini_cave_noise.png"),
    30: Image.open("./images/mini_deciduous_noise.png"),
    31: Image.open("./images/mini_desert_dirt_noise.png"),
    34: Image.open("./images/lavaarena_trim_mini.png"),
    42: Image.open("./images/mini_pebblebeach.png"),
    43: Image.open("./images/mini_meteor.png"),
    44: Image.open("./images/ground_noise_shellbeach.png").resize((256, 256)),
    201: Image.open("./images/mini_water_shallow.png"),
    202 :Image.new('RGB', (256, 256), (23,  51,  62)),
    203: Image.new('RGB', (256, 256), (14, 34, 61)),
    204: Image.new('RGB', (256, 256), (19, 20, 40)),
    205: Image.new('RGB', (256, 256), (40, 87, 93)),
    206: Image.open("./images/mini_water_coral.png"),
    207: Image.new('RGB', (256, 256), (8,   8,   14)),
    208: Image.new('RGB', (256, 256), (40, 87, 93)),
    257: Image.open("./images/ground_noise_monkeyisland.png").resize((256, 256)),
    260: Image.open("./images/mini_woodfloor_noise.png"),
    265: Image.open("./images/noise_mosaictiles_grey.png"),
    268: Image.open("./images/mini_carpet2_noise.png"),
}
per_num = 28
small_image_size = 9
cropped_images = {}
for key, value in image_paths.items():
    cropped_images[key] = []
    for i in range(per_num):
        array = []
        left = i * small_image_size
        for j in range(per_num):
            upper = j * small_image_size
            cropped_image = value.crop((left, upper, left + small_image_size, upper + small_image_size))
            array.append(cropped_image)
        cropped_images[key].append(array)

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

    big_image = Image.new('RGB', (3840, 3840))

    points_length = len(points)
    # dict = {}
    for i in range(points_length):
        left_num = i % per_num
        left_size = i * small_image_size
        for j in range(points_length):
            digit = int(points[i][j])
            if digit in image_paths:
                big_image.paste(cropped_images[digit][left_num][j%per_num],(left_size, j * small_image_size))
    #         else:
    #             if digit not in dict:
    #                 dict[digit] = 1
    #             else:
    #                 dict[digit] += 1
    # print(dict)
    big_image.show()

start = time.time()
get_map('Cluster_3')
end = time.time()
print(end - start)

