from flask import Flask

from controller.clusterController import clusterController
from controller.htmlController import htmlController
from controller.serverController import serverController
from controller.systemController import systemController

app = Flask(__name__)
app.register_blueprint(htmlController)
app.register_blueprint(serverController)
app.register_blueprint(clusterController)
app.register_blueprint(systemController)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
