from flask import Blueprint
from flask_cors import CORS

from service.chatService import ChatService

chatController = Blueprint('chatController', __name__)
CORS(chatController)
chatService = ChatService()


@chatController.route('/chat/<cluster_name>/<time>/<page_size>/<current_page>', methods=['GET'])
def get(cluster_name, time, page_size, current_page):
    return chatService.get(cluster_name, time, page_size, current_page)


