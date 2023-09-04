from flask import Flask
from flask_pymongo import MongoClient
from authlib.integrations.flask_client import OAuth

oauth = OAuth()
def create_app():
    app = Flask(__name__)

    app.url_map.strict_slashes = False
    app.secret_key = "testing"

    oauth.init_app(app)

    from .main.routes import bp_main as main
    from .users.routes import bp_users as users
    from .admin.routes import bp_admin as admin

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(admin)

    return app


def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    db = client.hadrumet
    return db