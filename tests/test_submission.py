import pytest
import pathlib, json

def sample_submissions_base():
    output_params = None
    with open(pathlib.Path(__file__).parent.absolute()/'data'/'sample_submissions_base.json') as samples:
        json_data = json.load(samples)
        output_params = [pytest.param(x['submission'], x['status_code'], id=x['id']) for x in json_data['sample_submissions']]

    return output_params

SAMPLE_SUBS = sample_submissions_base()

@pytest.mark.parametrize("submission, expected_code", SAMPLE_SUBS)
def test_submissions(client, submission, expected_code):
    """Tests some typical submissions to make sure the error code raised
    is the one expected (422 in a validation error)
    """
    rv = client.post('/v1/games/suggest', json=submission)
    assert rv.status_code == expected_code