"""Exception handlers to register on the API.
"""

from flask import current_app, jsonify


def handle_validation_error(error):
    """Handles validation errors raised by Marshmallow
    schema validation. Returns a 422 along with information
    about the validation errors.
    """

    return jsonify(
        message="The data submitted failed validation checks",
        issues=error.messages
    ), 422


def handle_database_error(error):
    """Handles uncaught database exceptions from SQLAlchemy.
    Returns a 500 but lets the user know it's because of the
    database.
    """

    current_app.logger.error(f'Database error: {error}')
    return jsonify(
        message="There was an issue communicating with the database"
    ), 500


def handle_invalid_usage(error):
    """Handles invalid usage of the API (e.g invalid query param entries).
    By default returns a 400 but this can be overriden when the exception
    is raised.
    """

    return jsonify(error.to_dict()), error.status_code