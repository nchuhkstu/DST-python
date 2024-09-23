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
    data = np.array(json.loads(points[1]), dtype=np.uint8)
    color_map = {
        3: (77, 64, 43),
        4: (117, 107, 87),
        5: (88, 67, 35),
        6: (60, 83, 51),
        7: (46, 53, 24),
        8: (46, 52, 82),
        30: (68, 52, 35),
        31: (115, 93, 49),
        34: (74, 67, 44),
        42: (74, 67, 44),
        43: (148, 209, 214),
        44: (75, 66, 44),
        201: (23, 51, 62),
        202: (23, 51, 62),
        203: (14, 34, 61),
        204: (19, 20, 40),
        205: (40, 87, 93),
        207: (8, 8, 14),
        208: (40, 87, 93),
    }
    colored_data = np.zeros((data.shape[0], data.shape[1], 3), dtype=np.uint8)
    for value, color in color_map.items():
        colored_data[data == value] = color
    img = Image.fromarray(colored_data)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return send_file(img_bytes, mimetype='image/png')