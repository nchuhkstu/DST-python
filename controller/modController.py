from flask import Blueprint
from flask_cors import CORS

from service.modService import ModService

modController = Blueprint('modController', __name__)
CORS(modController)
modService = ModService()


@modController.route('/<page_size>/<current_page>', methods=['GET'])
def get_mods(page_size, current_page):
    return modService.get_mods(page_size, current_page)




