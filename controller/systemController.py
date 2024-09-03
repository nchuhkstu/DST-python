from flask import Blueprint, request
from flask_cors import CORS

from service.systemService import SystemService

systemController = Blueprint('systemController', __name__)
CORS(systemController)
systemService = SystemService()


@systemController.route('/system', methods=['GET'])
def get():
    return systemService.get()


@systemController.route('/system', methods=['POST'])
def post():
    steamCMD_path = request.get_json().get('steamCMD_path')
    cluster_path = request.get_json().get('cluster_path')
    exe_path = request.get_json().get('exe_path')
    return systemService.post(steamCMD_path, cluster_path, exe_path)


@systemController.route('/system/information', methods=['GET'])
def information():
    return systemService.get_system_info()


@systemController.route('/system/downloading_steamCMD', methods=['GET'])
def downloading_steamCMD():
    return systemService.downloading_steamCMD()


@systemController.route('/system/update_game', methods=['GET'])
def update_game():
    return systemService.update_game()

