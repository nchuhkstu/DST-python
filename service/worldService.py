import os
import re

from utils.configLoader import g_variable


class WorldService:
    def __init__(self):
        self.get('Cluster_14')
        pass

    def submit(self):
        pass

    def get(self, cluster_name):
        overrides1 = {}
        overrides2 = {}
        overrides = {}
        path = os.path.join(g_variable["cluster_path"] + "/DST", cluster_name)
        with open(os.path.join(path, "Master", "leveldataoverride.lua"), "r", encoding='utf-8') as file:
            content = file.read()
        # 使用正则表达式提取 overrides 中的键值对
        pattern = r'overrides\s*=\s*\{([^}]*)\}'
        match = re.search(pattern, content)
        overrides_content = match.group(1)
        for line in overrides_content.split(','):
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                overrides1[key.strip()] = value.strip().strip('"')  # 去除多余空格和引号

        with open(os.path.join(path, "Caves", "leveldataoverride.lua"), "r", encoding='utf-8') as file:
            content = file.read()
        # 使用正则表达式提取 overrides 中的键值对
        pattern = r'overrides\s*=\s*\{([^}]*)\}'
        match = re.search(pattern, content)
        overrides_content = match.group(1)
        for line in overrides_content.split(','):
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                overrides2[key.strip()] = value.strip().strip('"')  # 去除多余空格和引号
        overrides['overrides1'] = overrides1
        overrides['overrides2'] = overrides2
        return overrides

    def post(self, cluster_name, setting):

        overrides1 = {key: value for d in setting['overrides1'] for key, value in d.items()}
        overrides2 = {key: value for d in setting['overrides2'] for key, value in d.items()}
        path = os.path.join(g_variable["cluster_path"] + "/DST", cluster_name)
        with open(os.path.join(path, "Master", "leveldataoverride.lua"), "r", encoding='utf-8') as file:
            lines = file.readlines()

        with open(os.path.join(path, "Master", "leveldataoverride.lua"), "w", encoding='utf-8') as file:
            for line in lines:
                updated = False
                stripped_line = line.lstrip()  # 去除左侧空格
                for key, value in overrides1.items():
                    if stripped_line.startswith(key + "="):
                        file.write(f'    {key}="{value}",\n')  # 写入更新后的行
                        updated = True
                        break
                if not updated:
                    file.write(line)
        with open(os.path.join(path, "Caves", "leveldataoverride.lua"), "r", encoding='utf-8') as file:
            lines = file.readlines()

        with open(os.path.join(path, "Caves", "leveldataoverride.lua"), "w", encoding='utf-8') as file:
            for line in lines:
                updated = False
                stripped_line = line.lstrip()  # 去除左侧空格
                for key, value in overrides2.items():
                    if stripped_line.startswith(key + "="):
                        file.write(f'    {key}="{value}",\n')  # 写入更新后的行
                        updated = True
                        break
                if not updated:
                    file.write(line)
        return {"status": "ok", "message": "世界设置已保存"}
        pass


