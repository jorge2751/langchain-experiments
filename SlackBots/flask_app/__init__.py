from flask import Flask

flask_app = Flask(__name__)
flask_app.secret_key = 'secret'