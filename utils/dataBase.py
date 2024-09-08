import sqlite3

from utils.global_variable import work_path

conn = sqlite3.connect(work_path + '/database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                 cluster_name TEXT,
                 userid TEXT,
                 name TEXT
                 )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS chat
                 (cluster_name TEXT,
                 name TEXT,
                 message TEXT,
                 message_type TEXT
                 )''')
conn.commit()
