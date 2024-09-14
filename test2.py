import requests

def query_files(page, num, text):
    url = "http://api.steampowered.com/IPublishedFileService/QueryFiles/v1/"
    params = {
        "key": "EBF3FBB49C03E71ABB75E6E3BFA35358",  # 替换为你的 Steam API 密钥
        "appid": "322330",
        "language": "6",
        "return_tags": "false",
        "return_vote_data": "false",
        "return_children": "true",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 若请求失败，抛出异常
        return response.json()  # 返回 JSON 格式的响应数据
    except requests.RequestException as e:
        print("请求失败:", e)
        return None

# 示例用法
result = query_files(page=1, num=10, text="")
print(result)