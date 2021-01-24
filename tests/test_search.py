"""Basic tests surrounding the site's search functionality.
"""

import pytest

@pytest.mark.parametrize('request_url', [
    '/v1/games/search?query=', '/v1/games/search'
])
def test_search_empty(client, request_url):
    """Empty searches should return an empty list.
    """

    rv = client.get(request_url)
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data['games'] == []


@pytest.mark.parametrize('search_param, number_of_results', [
    ('online', 5),
    ('among us', 1),
    ('deduction', 3),
    ('monopoly', 2)
])
def test_search_number_results(client, search_param, number_of_results):
    """Searching either words in a game's description or
    a title should return the correct number of results.
    """

    rv = client.get(f'/v1/games/search?query={search_param}')
    json_data = rv.get_json()
    assert len(json_data['games']) == number_of_results


@pytest.mark.parametrize('search_param', [
    'codewords', 'monopoly deal'
])
def test_specific_game_search(client, search_param):
    """Searching for a specific game title should return that game.
    """
    
    rv = client.get(f'/v1/games/search?query={search_param}')
    json_data = rv.get_json()

    assert json_data['games'][0]['name'].lower() == search_param