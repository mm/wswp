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


@pytest.mark.parametrize("players, free_only", [
    (4, 'true'),
    (4, 'false'),
    (1, 'true'),
    (1, 'true'),
    (10, 'false'),
    (10, 'true')
])
def test_random_game(client, players, free_only):
    """Tests to make sure the parameters sent to /random are respected.
    TODO: Need to set a seed for testing purposes so that this can be reproducible.
    """
    rv = client.get(f'/v1/games/random?players={players}&free_only={free_only}')
    response_json = rv.get_json()
    assert 'game' in response_json

    # Is the number of players we have in our party greater than the minimum number of players?
    assert players >= response_json['game']['min_players']
    # Is the number of players in our party not exceeding the max number of players?
    assert (response_json['game']['max_players'] is None) or (players <= response_json['game']['max_players'])
    # If we set free_only to be true, have we gotten a paid game?
    if free_only == 'true':
        assert response_json['game']['paid'] != True


@pytest.mark.parametrize("game_id, expected_code", [
    (1, 200),
    (24, 404)
])
def test_game_at_id(app, client, game_id, expected_code):
    """Tests to see if we can fetch a game at a specific ID, or a 404 if that game
    does not exist.
    """
    rv = client.get(f'/v1/games/{game_id}')
    assert rv.status_code == expected_code

    if expected_code == 200:
        game = rv.get_json().get('game')

        # Make sure the record from the database matches up
        with app.app_context():
            activity = Activity.query.get(game_id)
            assert game['id'] == activity.id
            assert game['name'] == activity.name
            assert game['description'] == activity.description
            assert game['paid'] == activity.paid
