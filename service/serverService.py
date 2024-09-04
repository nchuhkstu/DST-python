import ctypes
import os
import subprocess
import threading
import time

from utils.configLoader import g_variable
from utils.dataBase import conn
from utils.global_variable import lib, server_dict
# from utils.dataBase import conn
from utils.socketIO import socketIO


class ServerService:
    def __init__(self):
        self.process_num = 0
        self.lock = threading.Lock()
        self.exe_name = "dontstarve_dedicated_server_nullrenderer"
        self.conn = conn

    def process_cpu_usage_thread(self, cluster_name, world):
        while cluster_name in server_dict:
            if server_dict[cluster_name][world + '_process_index'] == 0:
                process_name = self.exe_name
            else:
                process_name = self.exe_name + "#" + str(server_dict[cluster_name][world + '_process_index'])
            usage = lib.cpuProcessUsage(ctypes.c_char_p(process_name.encode('utf-8')))
            socketIO.emit('process_cpu_usage', {
                'cluster_name': cluster_name,
                'world_name': world,
                'cpu_usage': usage.cpu,
                'memory_usage': usage.memory,
            })
        socketIO.emit('process_cpu_usage',
                      {'cluster_name': cluster_name, 'world_name': world, 'cpu_usage': 0, 'memory_usage': 0, })

    def execute_pipeline(self, world, cluster_name):
        command = self.exe_name + '.exe -console -cluster /DST/' + cluster_name + ' -shard ' + world
        os.chdir(g_variable["exe_path"] + '/bin')
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8',
                                errors='ignore', universal_newlines=True)
        with self.lock:
            if world == 'Master':
                server_dict.setdefault(cluster_name, {})['master_proc'] = proc
                server_dict[cluster_name]['master_process_index'] = self.process_num
            elif world == 'Caves':
                server_dict.setdefault(cluster_name, {})['caves_proc'] = proc
                server_dict[cluster_name]['caves_process_index'] = self.process_num
            self.process_num += 1
        server_dict[cluster_name]['current_players'] = 0
        while True:
            output = proc.stdout.readline()
            if output.strip() == '' and proc.poll() is not None:
                break
            if output:
                if world == 'Master':
                    if '[Join Announcement]' in output:
                        server_dict[cluster_name]['current_players'] += 1
                        # self.conn.cursor().execute(
                        #     "INSERT INTO chat (cluster_name, message, message_type) VALUES (cluster_name)")
                    elif '[Leave Announcement]' in output:
                        server_dict[cluster_name]['current_players'] -= 1
                    if ']:' in output:
                        socketIO.emit('log', {
                            "cluster_name": cluster_name,
                            "time": output.strip().split("]:")[0][1:],
                            "message": output.strip().split("]:")[1]
                        })
        return proc.poll()

    def start(self, cluster_name):
        if not os.path.exists(g_variable["exe_path"] + '/bin'):
            return {"status": "error", "message": "专用服务器路径错误，启动失败"}
        server_dict[cluster_name] = {"status": "运行中"}
        threading.Thread(target=self.execute_pipeline, args=('Master', cluster_name,)).start()
        while server_dict[cluster_name].get('master_process_index') is None:
            time.sleep(0.1)
        threading.Thread(target=self.process_cpu_usage_thread, args=(cluster_name, 'master')).start()

        threading.Thread(target=self.execute_pipeline, args=('Caves', cluster_name,)).start()
        while server_dict[cluster_name].get('caves_process_index') is None:
            time.sleep(0.1)
        threading.Thread(target=self.process_cpu_usage_thread, args=(cluster_name, 'caves')).start()
        return {"status": "ok", "message": "存档：" + cluster_name + " 启动成功"}

    def stop(self, cluster_name):
        if cluster_name not in server_dict:
            return {"status": "error", "message": f"存档：{cluster_name} 尚未启动"}

        server_dict[cluster_name]['master_proc'].terminate()
        server_dict[cluster_name]['caves_proc'].terminate()

        server_dict[cluster_name]['status'] = "未启动"
        max_index = max(server_dict[cluster_name]['master_process_index'],
                        server_dict[cluster_name]['caves_process_index'])
        del server_dict[cluster_name]

        for key, server in server_dict.items():
            if server['master_process_index'] > max_index:
                server_dict[key]['master_process_index'] = server_dict[key]['master_process_index'] - 2
                server_dict[key]['caves_process_index'] = server_dict[key]['caves_process_index'] - 2
        self.process_num = self.process_num - 2

        return {"status": "success", "message": f"{cluster_name} 已成功停止"}

    def pause(self):
        pass

    @staticmethod
    def save(cluster_name):
        if cluster_name not in server_dict:
            return {"status": "error", "message": f"存档：{cluster_name} 尚未启动"}
        server_dict[cluster_name]['master_proc'].stdin.write('c_save()' + '\n')
        server_dict[cluster_name]['master_proc'].stdin.flush()
        server_dict[cluster_name]['caves_proc'].stdin.write('c_save()' + '\n')
        server_dict[cluster_name]['caves_proc'].stdin.flush()
        return {"status": "ok", "message": "存档: " + cluster_name + "保存成功"}

    @staticmethod
    def backtrack(cluster_name, days):
        if cluster_name not in server_dict:
            return {"status": "error", "message": f"存档：{cluster_name} 尚未启动"}
        server_dict[cluster_name]['master_proc'].stdin.write('c_rollback(' + days + ' )' + '\n')
        server_dict[cluster_name]['master_proc'].stdin.flush()
        server_dict[cluster_name]['caves_proc'].stdin.write('c_rollback(' + days + ' )' + '\n')
        server_dict[cluster_name]['caves_proc'].stdin.flush()
        return {"status": "ok", "message": "存档: " + cluster_name + "正在回档中"}

    @staticmethod
    def custom_command(cluster_name, command):
        server_dict[cluster_name]['master_proc'].stdin.write(command + '\n')
        server_dict[cluster_name]['master_proc'].stdin.flush()
        server_dict[cluster_name]['caves_proc'].stdin.write(command + '\n')
        server_dict[cluster_name]['caves_proc'].stdin.flush()
        return {"status": "ok"}

    def remake(self):
        pass
