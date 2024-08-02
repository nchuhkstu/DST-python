from flask import Blueprint

from service.serverService import ServerService

serverController = Blueprint('serverController', __name__)
serverService = ServerService()


@serverController.route('/server/start/<cluster_name>', methods=['GET'])
def start(cluster_name):
    return serverService.start(cluster_name=cluster_name)


@serverController.route('/server/stop', methods=['GET'])
def stop():
    return serverService.stop()


@serverController.route('/server/save', methods=['GET'])
def stop():
    return serverService.stop()
