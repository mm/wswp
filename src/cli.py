"""Blueprint containing custom CLI commands to administer
the backend remotely.
"""

import click
import sqlalchemy
from flask import Blueprint

from seed import seed_game_entries
from src.model import Activity
from src.database import db

cli_bp = Blueprint('admin', __name__)


@cli_bp.cli.command('seed-db')
def seed_db():
    """Seeds game tables with data.
    """
    game_entries = seed_game_entries()

    for game in game_entries.get('games'):
        activity = Activity(**game)
        db.session.add(activity)

    click.echo("Games tables seeded.")
    db.session.commit()


@cli_bp.cli.command('clear-db')
def clear_db():
    """Clears all game data (users are unaffected)
    """

    if click.confirm("WARNING: This will delete ALL game data. Continue?"):
        text = sqlalchemy.text(
            """
            delete from activity;
            """
        )
        db.engine.execute(text)

        click.echo("Database cleared.")


@cli_bp.cli.command('backup-games')
def backup_games():
    """Creates a time-stamped JSON file of game and category tables,
    and pushes it to remote storage.
    """
    pass
