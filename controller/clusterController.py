from flask import Blueprint, request
from flask_cors import CORS

from service.clusterService import ClusterService

clusterController = Blueprint('clusterController', __name__)
CORS(clusterController)
clusterService = ClusterService()


@clusterController.route('/cluster', methods=['POST'])
def upload():
    file = request.files['file']
    return clusterService.upload(file)


@clusterController.route('/cluster/<cluster_name>', methods=['DELETE'])
def delete(cluster_name):
    return clusterService.delete(cluster_name=cluster_name)


@clusterController.route('/cluster/get', methods=['GET'])
def get():
    return clusterService.get()


@clusterController.route('/cluster/add', methods=['GET'])
def add():
    return clusterService.add()
