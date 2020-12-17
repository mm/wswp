import os

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import find_dotenv, load_dotenv

from src.routes import api
from src.cli import cli_bp


def create_app(config='src.config.DevConfig'):
    """Main application factory for WSWP. Will set up all config params,
    load up environment variables and bind things as needed (i.e. binding
    the app object to SQLAlchemy)

    Returns an application object.
    """

    # Our config classes make use of environment variables, so load
    # those first:
    if find_dotenv():
        load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config)

    from src.database import db
    from src.schema import ma
    db.init_app(app)
    from src.model import Category, Activity, Submission
    migrate = Migrate(app, db)
    ma.init_app(app)

    CORS(app)

    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(cli_bp)
    
    return app