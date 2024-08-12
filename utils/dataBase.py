# import sqlite3
# conn = sqlite3.connect('../database.db')
# cursor = conn.cursor()
# cursor.execute('''CREATE TABLE IF NOT EXISTS users
#                  (id INTEGER PRIMARY KEY,
#                  klei_id TEXT,
#                  user_name TEXT,
#                  survival_days INTEGER,
#                  survival_seconds INTEGER,
#                  role TEXT
#                  )''')
#
# cursor.execute('''CREATE TABLE IF NOT EXISTS chat
#                  (cluster_name TEXT,
#                  message TEXT,
#                  message_type TEXT
#                  )''')
# conn.commit()
# conn.close()
