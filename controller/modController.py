from flask import Blueprint, request
from flask_cors import CORS

from service.modService import ModService

modController = Blueprint('modController', __name__)
CORS(modController)
modService = ModService()


@modController.route('/mod/find', methods=['POST'])
def get_mods():
    page_size = request.form.get('pageSize')
    current_page = request.form.get('currentPage')
    content = request.form.get('content')
    return modService.get_mods(page_size, current_page, content)


@modController.route('/mod/<cluster_name>', methods=['GET'])
def get(cluster_name):
    return modService.get(cluster_name)


@modController.route('/mod/<cluster_name>/<mod_id>', methods=['GET'])
def enable(cluster_name, mod_id):
    return modService.enable(cluster_name, mod_id)


@modController.route('/mod/disable/<cluster_name>/<mod_id>', methods=['GET'])
def disable(cluster_name, mod_id):
    return modService.disable(cluster_name, mod_id)


@modController.route('/mod', methods=['POST'])
def focus_mod():
    mod_id = request.json.get('mod_id')
    img = request.json.get('img')
    title = request.json.get('title')
    author = request.json.get('author')
    href = request.json.get('href')
    return modService.focus_mod(mod_id, img, title, author, href)


@modController.route('/mod/<mod_id>', methods=['DELETE'])
def delete_mod(mod_id):
    return modService.delete(mod_id)
