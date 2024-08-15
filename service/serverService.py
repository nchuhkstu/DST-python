import ctypes
import os
import subprocess
import threading
import time

from controller.systemController import systemService
# from utils.dataBase import conn
from utils.socketIO import socketIO
from utils.systemInform import lib


class ServerService:
    def __init__(self):
        self.server_dict = {}
        self.process_num = 0
        self.lock = threading.Lock()
        # self.conn = conn

    def process_cpu_usage_thread(self, process_name, cluster_name, world):
        while self.server_dict[cluster_name][world + '_process_name'] is not None:
            usage = lib.cpuProcessUsage(ctypes.c_char_p(process_name.encode('utf-8')))
            socketIO.emit('process_cpu_usage', {
                'cluster_name': cluster_name,
                'world_name': world,
                'usage': usage
            })

    def execute_pipeline(self, world, cluster_name):
        exe_name = "dontstarve_dedicated_server_nullrenderer.exe "
        command = exe_name + '-console -cluster /DST/' + cluster_name + ' -shard ' + world
        os.chdir(systemService.exe_path)
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8',
                                errors='ignore', universal_newlines=True)
        with self.lock:
            if world == 'Master':
                self.server_dict.setdefault(cluster_name, {})['master_proc'] = proc
                if self.process_num == 0:
                    self.server_dict[cluster_name]['master_process_name'] = "dontstarve_dedicated_server_nullrenderer"
                else:
                    self.server_dict[cluster_name]['master_process_name'] = ("dontstarve_dedicated_server_nullrenderer#"
                                                                             + str(self.process_num))
            elif world == 'Caves':
                self.server_dict.setdefault(cluster_name, {})['caves_proc'] = proc
                if self.process_num == 0:
                    self.server_dict[cluster_name]['caves_process_name'] = "dontstarve_dedicated_server_nullrenderer"
                else:
                    self.server_dict[cluster_name]['caves_process_name'] = ("dontstarve_dedicated_server_nullrenderer#"
                                                                            + str(self.process_num))
            self.process_num += 1
        self.server_dict[cluster_name]['current_players'] = 0
        while True:
            output = proc.stdout.readline()
            if output.strip() == '' and proc.poll() is not None:
                break
            if output:
                if world == 'Master':
                    if '[Join Announcement]' in output:
                        self.server_dict[cluster_name]['current_players'] += 1
                        # self.conn.cursor().execute(
                        #     "INSERT INTO chat (cluster_name, message, message_type) VALUES (cluster_name)")
                    elif '[Leave Announcement]' in output:
                        self.server_dict[cluster_name]['current_players'] -= 1
                    if ']:' in output:
                        socketIO.emit('log', {
                            "cluster_name": cluster_name,
                            "time": output.strip().split("]:")[0][1:],
                            "message": output.strip().split("]:")[1]
                        })
        return proc.poll()

    def start(self, cluster_name):
        self.server_dict[cluster_name] = {"status": "运行中"}
        if not os.path.exists(systemService.exe_path):
            return {"status": "error", "message": "专用服务器可执行文件路径错误，启动失败"}
        threading.Thread(target=self.execute_pipeline, args=('Master', cluster_name,)).start()
        threading.Thread(target=self.execute_pipeline, args=('Caves', cluster_name,)).start()
        while self.server_dict[cluster_name].get('master_process_name') is None or self.server_dict[cluster_name].get(
                'caves_process_name') is None:
            time.sleep(0.1)
        threading.Thread(target=self.process_cpu_usage_thread,
                         args=(self.server_dict[cluster_name]['master_process_name'], cluster_name, 'master')).start()
        threading.Thread(target=self.process_cpu_usage_thread,
                         args=(self.server_dict[cluster_name]['caves_process_name'], cluster_name, 'caves')).start()
        return {"status": "ok", "message": "存档：" + cluster_name + " 启动成功"}

    def stop(self, cluster_name):
        if cluster_name not in self.server_dict:
            return {"status": "error", "message": "存档：" + cluster_name + " 尚未启动"}
        self.server_dict[cluster_name]['master_proc'].terminate()
        self.server_dict[cluster_name]['caves_proc'].terminate()
        self.server_dict[cluster_name]['status'] = "未启动"
        self.server_dict[cluster_name]['master_process_name'] = None
        self.server_dict[cluster_name]['caves_process_name'] = None
        self.process_num -= 2
        return {"status": "ok", "message": "存档：" + cluster_name + " 已停止"}

    def pause(self):
        pass

    def save(self, cluster_name):
        self.server_dict[cluster_name]['master_proc'].stdin.write('c_save()' + '\n')
        self.server_dict[cluster_name]['master_proc'].stdin.flush()
        self.server_dict[cluster_name]['caves_proc'].stdin.write('c_save()' + '\n')
        self.server_dict[cluster_name]['caves_proc'].stdin.flush()
        return {"status": "ok", "message": "存档: " + cluster_name + "保存成功"}

    def backtrack(self, cluster_name, days):
        self.server_dict[cluster_name]['master_proc'].stdin.write('c_rollback(' + days + ' )' + '\n')
        self.server_dict[cluster_name]['master_proc'].stdin.flush()
        self.server_dict[cluster_name]['caves_proc'].stdin.write('c_rollback(' + days + ' )' + '\n')
        self.server_dict[cluster_name]['caves_proc'].stdin.flush()
        return cluster_name + "rollback " + days

    def custom_command(self, cluster_name, command):
        self.server_dict[cluster_name]['master_proc'].stdin.write(command + '\n')
        self.server_dict[cluster_name]['master_proc'].stdin.flush()
        self.server_dict[cluster_name]['caves_proc'].stdin.write(command + '\n')
        self.server_dict[cluster_name]['caves_proc'].stdin.flush()
        return {"status": "ok"}

    def remake(self):
        pass
