import requests
from bs4 import BeautifulSoup


class ModService:
    def __init__(self):
        pass

    # 获取
    def get(self):
        pass

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
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
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
            mods[mod_id] = {
                'title': title,
                'author': author[3:],
                'img': img,
            }
        return mods

