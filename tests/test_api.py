"""Tests on public API routes.
"""

import pytest

from src.database import db
from src.model import Activity

def test_pulse(client):
    """Calls to /v1/pulse should return a 200.
    """
    
    rv = client.get('/v1/pulse')
    json_data = rv.get_json()
    assert rv.status_code == 200


def test_sql_assert(app):
    with app.app_context():
        games = Activity.query.filter_by(name="Among Us").all()
        assert len(games) == 1
