import os
import subprocess
import threading

from config import exe_name
from controller.systemController import systemService
from utils.dataBase import conn


class ServerService:
    def __init__(self):
        self.server_dict = {}
        self.conn = conn

    def execute_pipeline(self, world, cluster_name):
        command = exe_name + '-console -cluster /DST/' + cluster_name + ' -shard ' + world
        os.chdir(systemService.exe_path)
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8',
                                errors='ignore', universal_newlines=True)
        if world == 'Master':
            self.server_dict[cluster_name]['master_proc'] = proc
        elif world == 'Caves':
            self.server_dict[cluster_name]['caves_proc'] = proc
        self.server_dict[cluster_name]['current_players'] = 0
        while True:
            output = proc.stdout.readline()
            if output.strip() == '' and proc.poll() is not None:
                break
            if output:
                if world == 'Master':
                    if '[Join Announcement]' in output:
                        self.server_dict[cluster_name]['current_players'] += 1
                        self.conn.cursor().execute("INSERT INTO chat (cluster_name, message, message_type) VALUES (cluster_name)")
                    elif '[Leave Announcement]' in output:
                        self.server_dict[cluster_name]['current_players'] -= 1
                print(output.strip())
        return proc.poll()

    def start(self, cluster_name):
        if not os.path.exists(systemService.exe_path):
            print(systemService.exe_path)
            return "专用服务器可执行文件路径错误，启动失败"
        self.server_dict[cluster_name] = {
            'master_threading': threading.Thread(target=self.execute_pipeline, args=('Master', cluster_name,)).start(),
            'caves_threading': threading.Thread(target=self.execute_pipeline, args=('Caves', cluster_name,)).start(),
            'status': "运行中"}
        return "存档：" + cluster_name + " 启动成功"

    def stop(self, cluster_name):
        self.server_dict[cluster_name]['master_proc'].terminate()
        self.server_dict[cluster_name]['caves_proc'].terminate()
        self.server_dict[cluster_name]['status'] = "未启动"
        return cluster_name + "Server stopped"

    def pause(self):
        pass

    def save(self, cluster_name):
        self.server_dict[cluster_name]['master_proc'].stdin.write('c_save()' + '\n')
        self.server_dict[cluster_name]['master_proc'].stdin.flush()
        self.server_dict[cluster_name]['caves_proc'].stdin.write('c_save()' + '\n')
        self.server_dict[cluster_name]['caves_proc'].stdin.flush()
        return cluster_name + "Server saved"

    def backtrack(self, cluster_name, days):
        self.server_dict[cluster_name]['master_proc'].stdin.write('c_rollback(' + days + ' )' + '\n')
        self.server_dict[cluster_name]['master_proc'].stdin.flush()
        self.server_dict[cluster_name]['caves_proc'].stdin.write('c_rollback(' + days + ' )' + '\n')
        self.server_dict[cluster_name]['caves_proc'].stdin.flush()
        return cluster_name + "rollback " + days

    def remake(self):
        pass
