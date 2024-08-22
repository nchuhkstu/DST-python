from flask import Blueprint, request
from flask_cors import CORS

from service.worldService import WorldService

worldController = Blueprint('worldController', __name__)
CORS(worldController)
worldService = WorldService()


@worldController.route('/world', methods=['GET'])
def get(cluster_name):
    return worldService.get(cluster_name)


@worldController.route('/world', methods=['POST'])
def post(cluster_name):
    cluster_path = request.get_json().get('cluster_path')
    exe_path = request.get_json().get('exe_path')
    return worldService.post(cluster_path, exe_path)

