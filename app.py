from flask import Flask


from controller.clusterController import clusterController
from controller.htmlController import htmlController
from controller.serverController import serverController
from controller.systemController import systemController
from utils.socketIO import socketIO

app = Flask(__name__)
socketIO.init_app(app)
app.register_blueprint(htmlController)
app.register_blueprint(serverController)
app.register_blueprint(clusterController)
app.register_blueprint(systemController)


if __name__ == '__main__':
    socketIO.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
