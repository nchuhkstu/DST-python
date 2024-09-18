from utils.dataBase import conn


class ChatService:
    def __init__(self):
        pass

    @staticmethod
    def get(cluster_name, time, page_size, current_page):
        cursor = conn.cursor()
        offset = (int(current_page) - 1) * int(page_size)
        query = """SELECT * FROM chat
                       WHERE cluster_name = ? AND time <= ?
                       ORDER BY time DESC
                       LIMIT ? OFFSET ?"""
        values = (cluster_name, time, page_size, offset)
        cursor.execute(query, values)
        results = cursor.fetchall()
        messages = []
        for result in results:
            messages.append({
                "cluster_name": result[0],
                "name": result[1],
                "message": result[2],
                "message_type": result[3],
                "time": result[4]
            })
        cursor.close()
        return messages
