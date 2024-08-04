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
    cluster_path = request.get_json().get('cluster_path')
    exe_path = request.get_json().get('exe_path')
    return systemService.post(cluster_path, exe_path)

