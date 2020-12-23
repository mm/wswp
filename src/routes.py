"""
Blueprint containing all API resources for WSWP.
"""

from flask import Blueprint, jsonify, request, current_app
from marshmallow import ValidationError
from sqlalchemy import or_, column, text
from sqlalchemy.sql import functions
from sqlalchemy.exc import SQLAlchemyError
from src.model import Activity, Submission
from src.schema import ActivitySchema, SubmissionSchema
from src.database import db
from src.auth import requires_auth
import src.handlers as handlers
from src.exceptions import InvalidUsage, AuthError
from random import choice

api = Blueprint('api', __name__)
api.register_error_handler(ValidationError, handlers.handle_validation_error)
api.register_error_handler(InvalidUsage, handlers.handle_invalid_usage)
api.register_error_handler(AuthError, handlers.handle_auth_error)
api.register_error_handler(SQLAlchemyError, handlers.handle_database_error)


@api.route('/pulse', methods=['GET'])
def check_pulse():
    """Simple status check for the backend."""
    return jsonify(message="API is online"), 200


@api.route('/games', methods=['GET'])
def games():
    """Returns a list of games. Games are by default
    paginated to 30 items per page, and can be filtered
    via query params.

    Query params:
        - page: The page of games to fetch (int)
        - per_page: The number of items to fetch per page (int)
    """

    activity_schema = ActivitySchema()

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 30))
    except ValueError:
        raise InvalidUsage('page and per_page must both be integers greater than 0')
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
    ), 200


@api.route('/games/search', methods=['GET'])
def search_games():
    """Searches for games (either by title or description)
    
    Query Params:
        - query: Query terms to search for (string)
        - page: The page to access (int)
        - per_page: The number of results to return per page (int)
    """

    schema = ActivitySchema()
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 30))
    except ValueError:
        raise InvalidUsage('page and per_page must both be integers greater than 0')
    query = request.args.get('query')

    if query:
        db_results = Activity.search(query, page=page, per_page=per_page)
        results = schema.dump(db_results.results, many=True)

        return jsonify(
            games=results,
            page=page,
            total_pages=db_results.total_pages,
            next_page=db_results.next_page
        ), 200

    return jsonify(games=[], page=1, total_pages=1, next_page=None)


@api.route('/games/<int:id>', methods=['GET'])
def get_game(id):
    """Fetches a game by ID.
    """
    schema = ActivitySchema()

    # get_or_404 will immediately 404 if nothing was found
    game = Activity.query.get_or_404(id)

    return jsonify(game=schema.dump(game))


@api.route('/games/random', methods=['GET'])
def random_game():
    """Pulls a game at random (given some parameters
    to choose the game from -- passed in via URL
    parameters). Query params:

        - free_only: If true, only free games are shown
        - players: The number of players in the party
    """

    schema = ActivitySchema()

    # Validate our query param input:
    free_only = request.args.get('free_only', 'false')
    players = request.args.get('players')
    try:
        players = int(players)
    except ValueError:
        raise InvalidUsage("players must be an integer")
    if players < 1:
        raise InvalidUsage("players must be at least 1")

    # Pull IDs matching these conditions from the database:
    game_query = Activity.query

    # Find games such that min players <= players <= max_players
    # (max players can also be null in the case where a game has
    # a practically infinite # of players)
    game_query = game_query.filter(
        Activity.min_players <= players,
        or_(Activity.max_players >= players, column('max_players').is_(None))
    )

    # Add a filter against paid games if the user chooses:
    if free_only == 'true':
        game_query = game_query.filter(Activity.paid == False)
    
    # Get a list of primary key IDs representing the games:
    ids = [game.id for game in game_query.all()]
    
    # Then pick randomly from them:
    if len(ids) > 0:
        game = Activity.query.get(choice(ids))
        return jsonify(game=schema.dump(game)), 200
    else:
        return jsonify(message="No games found"), 404


@api.route('/games/suggest', methods=['POST'])
def consume_suggestion():
    """Pushes a game suggestion to the database. Expects a JSON
    payload conforming to the submission schema.
    """
    # Perform validation on what we receive:
    schema = SubmissionSchema()
    input_json = request.get_json()
    if not input_json:
        return InvalidUsage("Please submit a game")


    # For any empty strings, set them to None so our
    # schema validation catches it:
    for key, value in input_json.items():
        if input_json[key] == '':
            input_json[key] = None
    
    # Loading will perform validation checks -- if there's
    # a problem, we have a handler for this
    submission = schema.load(input_json)

    if submission['max_players'] == 0:
        submission['max_players'] = None


    # If we made it to this point, data passed validation checks
    # and we go ahead and try to submit to the database:
    try:
        db.session.add(Submission(**submission))
        db.session.commit()
        return jsonify(message="Submission added successfully"), 200
    except SQLAlchemyError:
        raise  # we have a handler for this declared up top
    except Exception as e:
        current_app.logger.error(f'Issue saving submission: {e}')
        return jsonify(message="Internal server error"), 500


@api.route('/admin/submissions/approve/<int:id>', methods=['GET'])
@requires_auth
def approve_submission(id, current_user=None):
    """Enables approval of game submissions from the admin
    panel. This marks the game as approved in the submissions table,
    and pushes it into the main activity table.
    """

    if not current_user:
        raise AuthError("You need to be authorized to access this endpoint")

    submission = Submission.query.get_or_404(id)

    try:
        game = Activity(
            name=submission.name,
            url=submission.url,
            description=submission.description,
            paid=submission.paid,
            min_players=submission.min_players,
            max_players=submission.max_players,
            submitted_by=submission.submitted_by
        )
        db.session.add(game)
        submission.approved = True
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Could not approve submission {id}")
        return jsonify(message="Could not approve submission"), 500
    
    return jsonify(message="Approved submission"), 200


@api.route('/admin/submissions/<int:id>', methods=['DELETE'])
@requires_auth
def archive_submission(id, current_user=None):
    """Marks a submission as archived. Archived submissions are regularly
    purged from the database.
    """

    if not current_user:
        raise AuthError("You need to be authorized to access this endpoint")

    submission = Submission.query.get_or_404(id)
    try:
        submission.archived = True
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'Could not archive submission {id}')
        return jsonify(message="Could not archive submission"), 500
    
    return jsonify(message="Archived submission"), 200


@api.route('/admin/submissions', methods=['GET'])
@requires_auth
def list_submissions(current_user=None):
    """Lists all submissions currently in the queue.
    """

    if not current_user:
        raise AuthError("You need to be authorized to access this endpoint")

    schema = SubmissionSchema()

    # Get all submissions that haven't been marked as archived
    # or approved:
    submission_query = Submission.query
    submission_query = submission_query.filter(
        Submission.archived != True,
        Submission.approved != True
    ).order_by(Submission.created_date.desc())

    results = schema.dump(submission_query.all(), many=True)
    
    return jsonify(submissions=results), 200

