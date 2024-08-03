import os
import subprocess
import threading

from config import exe_path, exe_name


class ServerService:
    def __init__(self):
        self.server_dict = {}

    def execute_pipeline(self, world, cluster_name):
        command = exe_name + '-console -cluster /DST/' + cluster_name + ' -shard ' + world
        os.chdir(exe_path)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, encoding='utf-8', errors='ignore')
        if world == 'Master':
            self.server_dict[cluster_name].master_proc = proc
        elif world == 'Caves':
            self.server_dict[cluster_name].caves_proc = proc
        while True:
            output = proc.stdout.readline()
            if output == '' and proc.poll() is not None:
                break
            if output:
                print(output.strip())
        return proc.poll()

    def start(self, cluster_name):
        self.server_dict[cluster_name] = {
            'master_threading': threading.Thread(target=self.execute_pipeline, args=('Master', cluster_name,)).start(),
            'caves_threading': threading.Thread(target=self.execute_pipeline, args=('Caves', cluster_name,)).start(),}

    def stop(self, cluster_name):
        self.server_dict[cluster_name].master_proc.terminate()
        self.server_dict[cluster_name].caves_proc.terminate()

    def pause(self):
        pass

    def save(self, cluster_name):
        self.server_dict[cluster_name].master_proc.stdin.write('c_save()' + '\n')
        self.server_dict[cluster_name].master_proc.stdin.flush()
        self.server_dict[cluster_name].caves_proc.stdin.write('c_save()' + '\n')
        self.server_dict[cluster_name].caves_proc.stdin.flush()

    def backtrack(self, cluster_name, days):
        self.server_dict[cluster_name].master_proc.stdin.write('c_rollback(' + days + ' )' + '\n')
        self.server_dict[cluster_name].master_proc.stdin.flush()
        self.server_dict[cluster_name].caves_proc.stdin.write('c_rollback(' + days + ' )' + '\n')
        self.server_dict[cluster_name].caves_proc.stdin.flush()

    def remake(self):
        pass


server = ServerService()
server.start('cluster_3')
