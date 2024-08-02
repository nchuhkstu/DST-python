from flask import Flask, render_template

from controller.htmlController import htmlController

app = Flask(__name__)
app.register_blueprint(htmlController)


if __name__ == '__main__':
    app.run()
