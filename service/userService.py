import os

from utils.configLoader import g_variable
from utils.global_function import update_user_data
from utils.global_variable import user, server_dict


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def get_users(cluster_name):
        update_user_data(cluster_name)
        return user[cluster_name]

    @staticmethod
    def set_admin(cluster_name, userid):
        path = os.path.join(g_variable["cluster_path"], cluster_name)
        with open(os.path.join(path, "adminlist.txt"), "r", encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if userid in line:
                    return {"status": "ok", "message": "已经是管理员了"}
        with open(os.path.join(path, "adminlist.txt"), "w", encoding='utf-8') as file:
            for line in lines:
                file.write(line)
            file.write(f'{userid}\n')
            return {"status": "ok", "message": "设置成功"}

    @staticmethod
    def delete_admin(cluster_name, userid):
        path = os.path.join(g_variable["cluster_path"], cluster_name)
        with open(os.path.join(path, "adminlist.txt"), "r", encoding='utf-8') as file:
            lines = file.readlines()
        with open(os.path.join(path, "adminlist.txt"), "w", encoding='utf-8') as file:
            for line in lines:
                if userid not in line:
                    file.write(line)
            return {"status": "ok", "message": "取消管理员成功"}

    @staticmethod
    def kick(cluster_name, userid):
        if cluster_name not in server_dict:
            return {"status": "ok", "message": f"存档：{cluster_name} 尚未启动"}
        server_dict[cluster_name]['master_proc'].stdin.write('kick ' + userid + '\n')
        server_dict[cluster_name]['master_proc'].stdin.flush()
        server_dict[cluster_name]['caves_proc'].stdin.write('kick ' + userid + '\n')
        server_dict[cluster_name]['caves_proc'].stdin.flush()
        return {"status": "ok", "message": "已踢出服务器"}
