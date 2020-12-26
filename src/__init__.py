import os

from flask import Flask
from flask_migrate import Migrate
from dotenv import find_dotenv, load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from src.routes import api
from src.cli import cli_bp
from src.auth import cors, limiter


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

    if app.config['ADMIN_OFF']:
        app.logger.info("Note: admin endpoints have been disabled!")

    # Configure Sentry logging. The DSN is read from the SENTRY_DSN
    # env variable, and the environment is read from the 
    # SENTRY_ENVIRONMENT variable
    sentry_sdk.init(
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.6
    )

    from src.database import db
    from src.schema import ma
    db.init_app(app)
    from src.model import Activity, Submission
    migrate = Migrate(app, db)
    ma.init_app(app)

    # Register cross-origin resource sharing and rate limiting modules:
    cors.init_app(app)
    limiter.init_app(app)

    # Associate all handlers of the Flask logger instance:
    for handler in app.logger.handlers:
        limiter.logger.addHandler(handler)

    app.register_blueprint(api, url_prefix='/v1')
    app.register_blueprint(cli_bp)
    
    return app