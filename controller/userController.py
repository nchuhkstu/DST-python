from flask import Blueprint, request
from flask_cors import CORS

from service.userService import UserService

userController = Blueprint('userController', __name__)
CORS(userController)
userService = UserService()


@userController.route('/user/<cluster_name>', methods=['GET'])
def get(cluster_name):
    return userService.get_users(cluster_name)



