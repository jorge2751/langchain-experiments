from flask_app.controllers import snapshot_bots
from flask_app import flask_app

if __name__ == '__main__':
    flask_app.run(debug=True, port=8080)