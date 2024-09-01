from flask import Blueprint, request
from flask_cors import CORS

from service.worldService import WorldService

worldController = Blueprint('worldController', __name__)
CORS(worldController)
worldService = WorldService()


@worldController.route('/world/<cluster_name>', methods=['GET'])
def get(cluster_name):
    return worldService.get(cluster_name)


@worldController.route('/world/<cluster_name>', methods=['POST'])
def post(cluster_name):
    setting = request.json['setting']
    return worldService.post(cluster_name, setting)

