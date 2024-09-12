from flask import Blueprint, request
from flask_cors import CORS

from service.modService import ModService

modController = Blueprint('modController', __name__)
CORS(modController)
modService = ModService()


@modController.route('/mod/<page_size>/<current_page>', methods=['GET'])
def get_mods(page_size, current_page):
    return modService.get_mods(page_size, current_page)


@modController.route('/mod', methods=['GET'])
def get():
    return modService.get()


@modController.route('/mod', methods=['POST'])
def focus_mod():
    mod_id = request.json.get('mod_id')
    img = request.json.get('img')
    title = request.json.get('title')
    author = request.json.get('author')
    return modService.focus_mod(mod_id, img, title, author)
