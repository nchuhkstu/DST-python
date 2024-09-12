import requests
from bs4 import BeautifulSoup
import sys

print("Python version:", sys.version)

def get_mods(page_size, current_page):
    url = (
            'https://steamcommunity.com/workshop/browse/?appid=322330&browsesort=trend&section=readytouseitems'
            '&actualsort=trend&p=' + str(current_page) + '&days=-1&numperpage=' + str(page_size))
    response = requests.get(url)
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
            'author': author,
            'img': img,
        }
    return mods


print(get_mods(18, 1))
