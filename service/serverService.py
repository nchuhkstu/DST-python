import os
import subprocess
import threading

from config import exe_path, exe_name


class ServerService:
    def __init__(self):
        self.cluster_name = None
        self.master_threading = threading.Thread(target=self.execute_pipeline, args=('Master',))
        self.caves_threading = threading.Thread(target=self.execute_pipeline, args=('Caves',))
        self.master_proc = None
        self.caves_proc = None

    def execute_pipeline(self, world):
        command = exe_name + '-console -cluster /DST/' + self.cluster_name + ' -shard ' + world
        os.chdir(exe_path)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, encoding='utf-8', errors='ignore')
        if world == 'Master':
            self.master_proc = proc
        elif world == 'Caves':
            self.caves_proc = proc
        while True:
            output = proc.stdout.readline()
            if output == '' and proc.poll() is not None:
                break
            if output:
                print(output.strip())
        return proc.poll()

    def start(self, cluster_name):
        self.cluster_name = cluster_name
        self.master_threading.start()
        self.caves_threading.start()

    def stop(self):
        self.master_proc.terminate()
        self.caves_proc.terminate()

    def pause(self):
        pass

    def save(self):
        self.master_proc.stdin.write('c_save()' + '\n')
        self.master_proc.stdin.flush()
        self.caves_proc.stdin.write('c_save()' + '\n')
        self.caves_proc.stdin.flush()

    def backtrack(self, days):
        self.master_proc.stdin.write('c_rollback(' + days + ' )' + '\n')
        self.master_proc.stdin.flush()
        self.caves_proc.stdin.write('c_rollback(' + days + ' )' + '\n')
        self.caves_proc.stdin.flush()

    def remake(self):
        pass


server = ServerService()
server.start('cluster_3')
