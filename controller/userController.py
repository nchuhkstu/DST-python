from flask import Blueprint, request
from flask_cors import CORS

from service.userService import UserService

userController = Blueprint('userController', __name__)
CORS(userController)
userService = UserService()


@userController.route('/user/<cluster_name>', methods=['GET'])
def get(cluster_name):
    return userService.get_users(cluster_name)


@userController.route('/user/set_admin/<cluster_name>/<userid>', methods=['GET'])
def set_admin(cluster_name, userid):
    return userService.set_admin(cluster_name, userid)


@userController.route('/user/delete_admin/<cluster_name>/<userid>', methods=['GET'])
def delete_admin(cluster_name, userid):
    return userService.delete_admin(cluster_name, userid)


@userController.route('/user/kick/<cluster_name>/<userid>', methods=['GET'])
def kick(cluster_name, userid):
    return userService.kick(cluster_name, userid)


