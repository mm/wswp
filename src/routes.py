"""
Blueprint containing all API resources for WSWP.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from src.model import Activity
from src.schema import ActivitySchema

from random import choice

api = Blueprint('api', __name__)


@api.route('/pulse', methods=['GET'])
def check_pulse():
    """Simple status check for the backend."""
    return jsonify(message="API is online"), 200


@api.route('/games', methods=['GET'])
def games():
    """Returns a list of games. Games are by default
    paginated to 25 items per page, and can be filtered
    via query params.
    """

    activity_schema = ActivitySchema()

    # TODO: Create an InvalidUsage exception to raise here:
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))
    show = request.args.get('price')

    # Begin building a query against the games table
    game_query = Activity.query

    # Filter out for only paid/free games if requested:
    if show in ['paid', 'free']:
        game_query = game_query.filter(
            Activity.paid == (show == 'paid')
        )

    # Order by date added and apply pagination
    game_query = game_query.order_by(
        Activity.created_date.desc()
    ).paginate(page=page, per_page=per_page)

    results = activity_schema.dump(game_query.items, many=True)
    return jsonify(
        games=results,
        page=game_query.page,
        total_pages=game_query.pages,
        next_page=game_query.next_num,
        per_page=per_page
    )


@api.route('/games/random', methods=['GET'])
def random_game():
    """Pulls a game at random (given some parameters
    to choose the game from -- passed in via URL
    parameters). Query params:

        - free_only: If true, only free games are shown
        - min: Minimum number of players (default 1)
        - max: Maximum number of players
    """

    schema = ActivitySchema()
    free_only = request.args.get('free_only', 'false')
    min_players = int(request.args.get('min', 1))
    max_players = request.args.get('max')

    # Pull IDs matching these conditions from the database:
    game_query = Activity.query

    if free_only == 'true':
        game_query = game_query.filter(Activity.paid == False)
    
    if max_players:
        game_query = game_query.filter(
            Activity.min_players >= min_players,
            Activity.max_players <= max_players
        )
    else:
        game_query = game_query.filter(Activity.min_players >= min_players)
    
    ids = [game.id for game in game_query.all()]
    
    if len(ids) > 0:
        game = Activity.query.get(choice(ids))
        return jsonify(game=schema.dump(game)), 200
    else:
        return jsonify(message="No games found"), 404


@api.route('/games/suggest', methods=['POST'])
def consume_suggestion():
    """Pushes a game suggestion to the database. Input
    data is form data.
    """

    return jsonify(message="Not yet implemented"), 501