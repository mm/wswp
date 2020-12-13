"""
Module containing all database table definitions.
"""

import datetime
from src.database import db
from sqlalchemy.dialects.postgresql import TEXT

class Category(db.Model):
    """Represents a category of games/activities. Not currently
    in use.
    """

    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256))
    activities = db.relationship('Activity', backref='category')


class Activity(db.Model):
    """Represents an activity (i.e. a game)
    """

    __tablename__ = 'activity'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    name = db.Column(db.String(1024), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    description = db.Column(TEXT, nullable=True)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    price_desc = db.Column(db.String(100), nullable=True)
    min_players = db.Column(db.Integer, nullable=False, default=1)
    max_players = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    submitted_by = db.Column(db.String(256), nullable=True)


class Submission(db.Model):
    """Represents a community submission to the game/activity index.
    """

    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1024), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    description = db.Column(TEXT, nullable=True)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    price_desc = db.Column(db.String(100), nullable=True)
    min_players = db.Column(db.Integer, nullable=False, default=1)
    max_players = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    submitted_by = db.Column(db.String(256), nullable=True)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    archived = db.Column(db.Boolean, nullable=False, default=False)