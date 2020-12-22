"""
Module containing all database table definitions.
"""

import datetime, math
from src.database import db
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy import func, text
from collections import namedtuple

paginated_results = namedtuple('PaginatedSearchResults', ['results', 'page', 'next_page', 'total_pages'])

class Activity(db.Model):
    """Represents an activity (i.e. a game)
    """

    __tablename__ = 'activity'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1024), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    description = db.Column(TEXT, nullable=True)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    min_players = db.Column(db.Integer, nullable=False, default=1)
    max_players = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    submitted_by = db.Column(db.String(256), nullable=True)

    @classmethod
    def search(cls, search_term, page=1, per_page=25):
        """Queries Activity objects whose name / description
        match a certain search_term, applying pagination as adjusted by
        the page and per_page parameters (uses PostgreSQL full-text
        search under the hood)

        Returns a NamedTuple, containing the results (list), current page,
        next page, and total number of pages. 
        """

        # Check to see the total number of results for our search
        all_results_count = """
                select count(1)
                from activity
                where to_tsvector(name || ' ' || coalesce(description, '')) @@ plainto_tsquery(:searchparam)
        """
        number_of_records = db.engine.execute(text(all_results_count).bindparams(searchparam=search_term)).fetchone()[0]

        # If we don't have any results off the bat, don't even bother paginating:
        if number_of_records < 1:
            return paginated_results([], 1, None, 1)

        # Otherwise, paginate!
        if (number_of_records / per_page) < 1:
            total_pages = 1
        else:
            total_pages = 1 + math.floor(number_of_records / per_page)
        
        # These will be used in our SQL query:
        limit = per_page
        offset = (page - 1) * per_page

        if (page + 1) > total_pages:
            next_page = None
        else:
            next_page = page + 1 

        results = db.session.query(cls).from_statement(text(
            """select * 
            from activity
            where to_tsvector(name || ' ' || coalesce(description, '')) @@ plainto_tsquery(:searchparam)
            limit :limit offset :offset
            """
        )).params(searchparam=search_term, limit=limit, offset=offset).all()
        
        return paginated_results(results, page, next_page, total_pages)


class Submission(db.Model):
    """Represents a community submission to the game/activity index.
    """

    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1024), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    description = db.Column(TEXT, nullable=True)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    min_players = db.Column(db.Integer, nullable=False, default=1)
    max_players = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    submitted_by = db.Column(db.String(256), nullable=True)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    archived = db.Column(db.Boolean, nullable=False, default=False)