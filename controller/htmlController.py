from flask import Blueprint, render_template

htmlController = Blueprint('htmlController', __name__)


@htmlController.route('/')
def home():
    return render_template('index.html')


@htmlController.route('/', defaults={'path': ''})
@htmlController.route('/<path:path>')
def home2(path):
    return render_template('index.html')
