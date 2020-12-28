"""Tests on /games API routes. Search and suggestion
routes are covered in other modules.
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


# def test_sql_assert(app):
#     with app.app_context():
#         games = Activity.query.filter_by(name="Among Us").all()
#         assert len(games) == 1


def test_games_default(client):
    """Based on the seed data provided (and default pagination settings),
    a call to /games with no parameters should return all games.
    """

    rv = client.get('/v1/games')
    json_data = rv.get_json()

    assert rv.status_code == 200
    assert len(json_data['games']) == 13
    assert json_data['next_page'] is None
    assert json_data['total_pages'] == 1


@pytest.mark.parametrize("page,per_page,exp_games,exp_next_page,exp_status_code", [
    (1, 25, 13, None, 200),
    (2, 25, None, None, 404),
    (1, 10, 10, 2, 200),
    (2, 10, 3, None, 200)
])
def test_pagination(client, page, per_page, exp_games, exp_next_page, exp_status_code):
    """Tests to make sure the right amount of items are being returned
    when using pagination.
    """
    
    rv = client.get(f'/v1/games?page={page}&per_page={per_page}')
    assert rv.status_code == exp_status_code
    if exp_status_code == 200:
        json_data = rv.get_json()
        assert len(json_data['games']) == exp_games
        assert json_data['next_page'] == exp_next_page


@pytest.mark.parametrize("page, per_page, exp_status_code", [
    (1, 25, 200),
    (-1, 10, 400),
    ('a', 'b', 400),
    (2, -4, 400),
    (2, 'b', 400)
])
def pagination_query_validation(client, page, per_page, exp_status_code):
    """Tests to make sure page and per_page params are validated. Invalid
    params should return a 400 error.
    """

    rv = client.get(f'/v1/games?page={page}&per_page={per_page}')
    assert rv.status_code == exp_status_code