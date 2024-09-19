import os
import shutil
import subprocess
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

from utils.configLoader import g_variable
from utils.dataBase import conn


class ModService:
    def __init__(self):
        pass

    @staticmethod
    def get(cluster_name):
        path = os.path.join(g_variable["cluster_path"], cluster_name, "Master", "modoverrides.lua")
        enabled_mods = {}
        with open(path, "r", encoding='utf-8') as file:
            for line in file:
                if "workshop-" in line:
                    start_index = line.find('-')
                    end_index = line.rfind('"')
                    mod_id = line[start_index + 1:end_index]
                    enabled_mods[mod_id] = True
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
                "content": exist[4],
                "href": exist[5],
                "status": exist[0] in enabled_mods
            }
            mods.append(mod)
        cursor.close()
        return mods

    @staticmethod
    def enable(cluster_name, mod_id):
        path = os.path.join(g_variable["cluster_path"], cluster_name, "Master", "modoverrides.lua")
        path2 = os.path.join(g_variable["cluster_path"], cluster_name, "Caves", "modoverrides.lua")
        with open(path, "r", encoding='utf-8') as file:
            lines = file.readlines()
        lines[-2] = lines[-2] + '\t["workshop-' + mod_id + '"]={\n\t\tenabled=true\n\t},\n'
        with open(path, "w", encoding='utf-8') as file:
            file.writelines(lines)
        with open(path2, "w", encoding='utf-8') as file:
            file.writelines(lines)
        return {"status": "ok", "message": "Enabled mod"}

    @staticmethod
    def disable(cluster_name, mod_id):
        path = os.path.join(g_variable["cluster_path"], cluster_name, "Master", "modoverrides.lua")
        path2 = os.path.join(g_variable["cluster_path"], cluster_name, "Caves", "modoverrides.lua")
        with open(path, "r", encoding='utf-8') as file:
            lines = file.readlines()
            flag1, flag2 = 0, 0
            start_line, end_line = 1, 1
            for line_number, line in enumerate(lines, start=1):  # 从1开始计数
                if mod_id in line:
                    flag1 = 1
                    start_line = line_number
                elif flag1 == 1 and 'enabled=true' in line:
                    flag2 = 1
                elif flag2 == 1 and '}' in line:
                    end_line = line_number
                    break
        lines = lines[:start_line - 1] + lines[end_line:]
        with open(path, "w", encoding='utf-8') as file:
            file.writelines(lines)
        with open(path2, "w", encoding='utf-8') as file:
            file.writelines(lines)
        return {"status": "ok", "message": "Enabled mod"}

    @staticmethod
    def delete(mod_id):
        cursor = conn.cursor()
        query = "DELETE FROM mods WHERE mod_id = ?;"
        cursor.execute(query, (mod_id,))
        conn.commit()
        cursor.close()
        mod_path = os.path.join(g_variable["mod_path"], "workshop-" + mod_id)
        shutil.rmtree(mod_path)
        return {"status": "ok", "message": "取消订阅成功"}

    @staticmethod
    def get_mods(page_size, current_page, content):
        url = (
                'https://steamcommunity.com/workshop/browse/?appid=322330&browsesort=trend&section=readytouseitems'
                '&actualsort=trend&p=' + str(current_page) + '&days=-1&numperpage=' + str(page_size)) \
            if content == '' \
            else (
                'https://steamcommunity.com/workshop/browse/?appid=322330&searchtext=' + content +
                '&browsesort=trend&section=readytouseitems&created_date_range_filter_start=0'
                '&created_date_range_filter_end=0'
                '&updated_date_range_filter_start=0&updated_date_range_filter_end=0&actualsort=trend&days=-1'
                '&p=' + str(current_page) + '&numperpage=' + str(page_size))
        print(url)
        headers = {'Accept-language': 'zh-CN,zh;q=0.9',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/128.0.0.0 Safari/537.36'}
        try:
            proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
            try:
                response = requests.get(url, proxies=proxies, headers=headers)
            except requests.exceptions.ProxyError:
                response = requests.get(url, headers=headers)
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
    def focus_mod(mod_id, img, title, author, href):
        if not os.path.exists(g_variable["exe_path"]):
            os.makedirs(g_variable["exe_path"], exist_ok=True)
        full_command = (f'{g_variable["steamCMD_path"]}/steamcmd.exe +force_install_dir '
                        f'"{g_variable["mod_path"]}" +login anonymous +workshop_download_item 322330 {mod_id} +quit')

        proc = subprocess.Popen(full_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8',
                                errors='ignore', universal_newlines=True, bufsize=1)
        while True:
            time.sleep(0.1)
            line = proc.stdout.readline()
            print(line)
            if 'Success' in line:
                break
            elif 'Failure' in line:
                return {"status": "error", "message": "订阅失败,未知错误"}
            elif 'Timeout' in line:
                return {"status": "error", "message": "订阅失败,连接超时，请重试"}

        source_path = os.path.join(g_variable["mod_path"], "steamapps", "workshop", "content", "322330", mod_id)
        if not os.path.exists(source_path):
            return {"status": "error", "message": "订阅失败"}
        target_path = os.path.join(g_variable["mod_path"], "workshop-" + mod_id)
        shutil.move(str(source_path), str(target_path))
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
            INSERT INTO mods(mod_id, img, title, author, content, href)
            SELECT ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM mods WHERE mod_id = ?
            )
        """
        values = (mod_id, img, title, author, str(content), href, mod_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return {"status": "ok", "message": "订阅成功"}
