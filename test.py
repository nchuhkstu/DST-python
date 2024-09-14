import requests

class ModInfo:
    def __init__(self, id, name, author, desc, time, sub, img):
        self.ID = id
        self.Name = name
        self.Author = author
        self.Desc = desc
        self.Time = time
        self.Sub = sub
        self.Img = img

def search_mod_info_by_workshop_id(mod_id):
    url = "http://api.steampowered.com/IPublishedFileService/GetDetails/v1/"
    params = {
        "key": "EBF3FBB49C03E71ABB75E6E3BFA35358",  # 替换为你的 Steam API 密钥
        "language": "6",
        "publishedfileids[0]": mod_id,
        "return_children": "true",
        "return_vote_data": "true",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    result = response.json()
    print(result['response']['publishedfiledetails'][0])


mod_info = search_mod_info_by_workshop_id(1098843500)