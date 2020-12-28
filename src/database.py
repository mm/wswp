from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# This is initially blank -- in the main application factory,
# it's bound to our Flask application.
db = SQLAlchemy()