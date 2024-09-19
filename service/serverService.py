import ctypes
import os
import subprocess
import threading
import time
import uuid
import requests
import urllib.request
import json
from utils.configLoader import g_variable
from utils.dataBase import conn
from utils.global_function import update_user_data
from utils.global_variable import lib, server_dict, cache
from utils.socketIO import socketIO
from lupa import LuaRuntime
from utils.global_variable import user

lua = LuaRuntime(unpack_returned_tuples=True)


class ServerService:
    def __init__(self):
        self.process_num = 0
        self.lock = threading.Lock()
        self.exe_name = "dontstarve_dedicated_server_nullrenderer"
        self.last_modified_times = {}
        self.send_threads = {}

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
                    if 'Client authenticated' in output:
                        start_index = output.find('(')
                        userid = output[start_index + 1:start_index + 12]
                        name = output[start_index + 14:-1]

                        cursor = conn.cursor()
                        query = """
                            INSERT INTO users(cluster_name, userid, name) 
                            SELECT ?, ?, ? 
                            WHERE NOT EXISTS (
                                SELECT 1 FROM users WHERE userid = ? AND cluster_name = ?
                            )
                        """
                        values = (cluster_name, userid, name, userid, cluster_name)
                        cursor.execute(query, values)
                        conn.commit()
                        cursor.close()
                    if '[Join Announcement]' in output:
                        start_index = output.rfind(' ')
                        name = output[start_index + 1:-1]
                        server_dict[cluster_name]['current_players'] += 1
                        if cluster_name not in cache:
                            cache[cluster_name] = []
                        if name not in cache[cluster_name]:
                            cache[cluster_name].append(name)
                        for key, value in user[cluster_name].items():
                            if value["name"] == name:
                                value["online"] = "online"
                        socketIO.emit('server_update_current_players', {
                            "cluster_name": cluster_name,
                            "current_players": server_dict[cluster_name]['current_players'],
                        })
                    elif '[Leave Announcement]' in output:
                        start_index = output.rfind(' ')
                        name = output[start_index + 1:-1]
                        cache[cluster_name].remove(name)
                        server_dict[cluster_name]['current_players'] -= 1
                        for key, value in user[cluster_name].items():
                            if value["name"] == name:
                                value["online"] = "outline"
                        socketIO.emit('server_update_current_players', {
                            "cluster_name": cluster_name,
                            "current_players": server_dict[cluster_name]['current_players'],
                        })
                    elif 'INVALID_TOKEN' in output:
                        server_dict[cluster_name]['status'] = "令牌错误"
                        socketIO.emit('server_update_status', {
                            "cluster_name": cluster_name,
                            "status": server_dict[cluster_name]['status'],
                        })
                    elif 'shard mode startup: RakNet UDP startup failed: SOCKET_PORT_ALREADY_IN_USE' in output:
                        server_dict[cluster_name]['status'] = "通信端口错误"
                        socketIO.emit('server_update_status', {
                            "cluster_name": cluster_name,
                            "status": server_dict[cluster_name]['status'],
                        })
                    elif 'SOCKET_PORT_ALREADY_IN_USE' in output:
                        server_dict[cluster_name]['status'] = "世界端口被占用"
                        socketIO.emit('server_update_status', {
                            "cluster_name": cluster_name,
                            "status": server_dict[cluster_name]['status'],
                        })
                    elif 'Sim paused' in output:
                        if server_dict[cluster_name]['status'] != "通信端口被占用":
                            server_dict[cluster_name]['status'] = "运行中"
                            socketIO.emit('server_update_status', {
                                "cluster_name": cluster_name,
                                "status": server_dict[cluster_name]['status'],
                            })
                    elif '[Say]' in output:
                        start_index = output.find(')')
                        end_index = output.rfind(': ')
                        name = output[start_index + 2:end_index]
                        message = output[end_index + 2:-1]
                        message_type = 'chat'
                        cursor = conn.cursor()
                        query = """INSERT INTO chat(cluster_name, name, message, message_type, time)
                                        VALUES (?, ?, ?, ?, ?)
                                """
                        values = (cluster_name, name, message, message_type, time.time())
                        cursor.execute(query, values)
                        conn.commit()
                        cursor.close()
                        socketIO.emit('chat', {
                            "cluster_name": cluster_name,
                            "name": name,
                            "message": message,
                            "message_type": message_type,
                            "time": time.time()
                        })
                    if ']:' in output:
                        socketIO.emit('log', {
                            "cluster_name": cluster_name,
                            "time": output.strip().split("]:")[0][1:],
                            "message": output.strip().split("]:")[1]
                        })
        return proc.poll()

    @staticmethod
    def update_user_data_running(cluster_name):
        while cluster_name in server_dict:
            update_user_data(cluster_name)
            socketIO.emit('user', user[cluster_name])
            time.sleep(480)

    def start(self, cluster_name):
        if not os.path.exists(g_variable["exe_path"] + '/bin'):
            return {"status": "error", "message": "专用服务器路径错误，启动失败"}
        server_dict[cluster_name] = {"status": "启动中"}

        threading.Thread(target=self.update_user_data_running, args=(cluster_name,)).start()

        threading.Thread(target=self.execute_pipeline, args=('Master', cluster_name,)).start()
        while server_dict[cluster_name].get('master_process_index') is None:
            time.sleep(0.1)
        threading.Thread(target=self.process_cpu_usage_thread, args=(cluster_name, 'master')).start()

        threading.Thread(target=self.execute_pipeline, args=('Caves', cluster_name,)).start()
        while server_dict[cluster_name].get('caves_process_index') is None:
            time.sleep(0.1)
        threading.Thread(target=self.process_cpu_usage_thread, args=(cluster_name, 'caves')).start()

        self.send_threads[cluster_name] = threading.Thread(target=self.send_remote_start, args=(cluster_name,))
        self.send_threads[cluster_name].start()

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
    def send_remote_start(cluster_name):
        key = str(uuid.uuid4())
        with open(os.path.join(g_variable["cluster_path"], cluster_name, "cluster.ini"), 'r',
                  encoding='utf-8') as file:
            for line in file:
                if "cluster_name" in line:
                    room_name = line.split(" = ")[1].strip()
                    break
        while cluster_name in server_dict:
            data = {
                "key": key,
                "room_name": room_name,
                "time": int(time.time()),
                "version": '1.4.0'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/58.0.3029.110 Safari/537.3'}
            try:
                response = requests.post("http://8.138.88.84:10000/start", headers=headers, json=data, timeout=5,
                                         verify=False)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                pass
            time.sleep(1)

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
