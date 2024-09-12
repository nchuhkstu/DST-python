import requests
from bs4 import BeautifulSoup
from utils.dataBase import conn


class ModService:
    def __init__(self):
        pass

    @staticmethod
    def get():
        cursor = conn.cursor()
        query = "SELECT * FROM mods"
        cursor.execute(query)
        exists = cursor.fetchall()  # 获取查询结果
        mods = []
        for exist in exists:
            mod = {
                "mod_id": exist[0],
                "img": exist[1],
                "title": exist[2],
                "author": exist[3],
                "content": exist[4]
            }
            mods.append(mod)
        cursor.close()
        return mods

    def add(self):
        pass

    def delete(self):
        pass

    def download(self):
        pass

    @staticmethod
    def get_mods(page_size, current_page):
        url = (
                'https://steamcommunity.com/workshop/browse/?appid=322330&browsesort=trend&section=readytouseitems'
                '&actualsort=trend&p=' + str(current_page) + '&days=-1&numperpage=' + str(page_size))
        try:
            response = requests.get(url, proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
            return {}
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        elements_with_special_class = soup.find_all(class_='workshopItem')

        mods = {}
        for element in elements_with_special_class:
            mod_id = element.find(class_='ugc').get('data-publishedfileid')
            title = element.find(class_='workshopItemTitle ellipsis').text
            author = element.find(class_='workshopItemAuthorName ellipsis').text
            img = element.find(class_='workshopItemPreviewImage').get('src')
            href = element.find(class_='ugc').get('href')
            cursor = conn.cursor()
            # 查询 mod_id 是否存在
            check_query = "SELECT COUNT(1) FROM mods WHERE mod_id = ?;"
            cursor.execute(check_query, (mod_id,))
            exists = cursor.fetchone()[0]  # 获取查询结果
            cursor.close()
            focus = exists > 0
            mods[mod_id] = {
                'title': title,
                'author': author[3:],
                'img': img,
                'href': href,
                'mod_id': mod_id,
                'focus': focus
            }
        return mods

    @staticmethod
    def focus_mod(mod_id, img, title, author):
        print('focus_mod:', mod_id, title, author)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/128.0.0.0 Safari/537.36", "content-type": "text/html;charset=UTF-8",
                   "Vary": "Accept-Encoding", "Accept-Language": "zh-CN,zh;q=0.9"}
        url = 'https://steamcommunity.com/sharedfiles/filedetails/?id=' + str(mod_id)
        try:
            response = requests.get(url, headers=headers,
                                    proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'})
            response.raise_for_status()  # Raise an HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": "订阅失败:" + str(e)}
        response.encoding = 'utf-8'
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find(class_='detailBox altFooter')
        cursor = conn.cursor()
        query = """
            INSERT INTO mods(mod_id, img, title, author, content)
            SELECT ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM mods WHERE mod_id = ?
            )
        """
        values = (mod_id, img, title, author, str(content), mod_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return {"status": "ok", "message": "订阅成功"}
