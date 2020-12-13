import os

from flask import Flask
from flask_migrate import Migrate
from dotenv import find_dotenv, load_dotenv

from src.routes import api


def create_app():
    """Main application factory for WSWP. Will set up all config params,
    load up environment variables and bind things as needed (i.e. binding
    the app object to SQLAlchemy)

    Returns an application object.
    """

    if find_dotenv():
        load_dotenv()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from src.database import db
    from src.schema import ma
    db.init_app(app)
    from src.model import Category, Activity
    migrate = Migrate(app, db)
    ma.init_app(app)

    app.register_blueprint(api, url_prefix='/api')

    return app