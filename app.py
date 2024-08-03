from flask import Flask

from controller.htmlController import htmlController
from controller.serverController import serverController

app = Flask(__name__)
app.register_blueprint(htmlController)
app.register_blueprint(serverController)


if __name__ == '__main__':
    app.run()
