from flask import Flask

from controller.clusterController import clusterController
from controller.htmlController import htmlController
from controller.serverController import serverController
from controller.systemController import systemController
from controller.userController import userController
from controller.worldController import worldController
from utils.configLoader import g_variable
from utils.socketIO import socketIO

app = Flask(__name__)
socketIO.init_app(app)
app.register_blueprint(htmlController)
app.register_blueprint(serverController)
app.register_blueprint(clusterController)
app.register_blueprint(systemController)
app.register_blueprint(worldController)
app.register_blueprint(userController)


if __name__ == '__main__':
    socketIO.run(app, host='0.0.0.0', port=g_variable["port"], allow_unsafe_werkzeug=True)
