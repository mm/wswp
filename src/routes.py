"""
Blueprint containing all API resources for WSWP.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from src.model import Activity
from src.schema import ActivitySchema

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