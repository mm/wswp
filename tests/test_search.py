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


