"""Tests for submission functionality-- primarily if a submission
form is validated properly and passed to the backend.
"""

import pytest
import pathlib, json
from src.model import Activity, Submission

# Load in sample submissions and their expected status codes if they were submitted:
with open(pathlib.Path(__file__).parent.absolute()/'data'/'sample_submissions_base.json') as samples:
    json_data = json.load(samples)
    sample_submissions = [pytest.param(x['submission'], x['status_code'], x.get('broken_field'), id=x['id']) for x in json_data['sample_submissions']]


@pytest.mark.parametrize("submission, expected_code, problematic_field", sample_submissions)
def test_submissions(app, client, submission, expected_code, problematic_field):
    """Tests some typical submissions to make sure the error code raised
    is the one expected (422 in a validation error) and that any validation
    errors raised correspond to the right field that failed validation.
    """
    rv = client.post('/v1/games/suggest', json=submission)
    response_json = rv.get_json()
    assert rv.status_code == expected_code
    # In the response, validation issues are given in the 'issues' object, like:
    # .. 'issues': { 'url': ['Field may not be null'] }
    # So, we check to see if the issues object contains the field we expected
    # to trigger a validation error.
    if 'issues' in response_json and problematic_field:
        assert problematic_field in response_json['issues']
    # If we expected a 200, was the submission actually added?
    if expected_code == 200:
        with app.app_context():
            game = Submission.query.filter_by(name=submission['name']).first()
            assert game is not None


@pytest.mark.parametrize("max_players", [0, None])
def test_blank_max_players(app, client, max_players):
    """Leaving the max number of players blank (or 0) should result
    in a NULL value going to the database.
    """
    submission = {
        "name": "TestMaxPlayersBlank",
        "url": "https://google.ca",
        "description": "test desc",
        "min_players": 4,
        "max_players": max_players,
        "paid": False,
        "submitted_by": "Matt"
    }
    rv = client.post('/v1/games/suggest', json=submission)
    assert rv.status_code == 200

    with app.app_context():
        # Physically go into the submissions table and ensure the created
        # record has NULL max_players
        game = Submission.query.filter_by(name="TestMaxPlayersBlank").first()
        assert game.max_players is None
