from flask import Blueprint
from flask_cors import CORS

from service.serverService import ServerService

serverController = Blueprint('serverController', __name__)
CORS(serverController)
serverService = ServerService()



@serverController.route('/server/start/<cluster_name>', methods=['GET'])
def start(cluster_name):
    return serverService.start(cluster_name=cluster_name)


@serverController.route('/server/stop/<cluster_name>', methods=['GET'])
def stop(cluster_name):
    return serverService.stop(cluster_name=cluster_name)


@serverController.route('/server/save/<cluster_name>', methods=['GET'])
def save(cluster_name):
    return serverService.save(cluster_name=cluster_name)


@serverController.route('/server/backtrack/<cluster_name>/<days>', methods=['GET'])
def backtrack(cluster_name, days):
    return serverService.backtrack(cluster_name=cluster_name, days=days)
