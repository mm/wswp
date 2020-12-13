"""Module to seed the database with data.
"""

from typing import List, Dict
import pathlib
import json

def seed_game_entries() -> List[Dict]:
    """Consumes a `seed.json` file and outputs a list of dicts
    """
    data = None

    with open(pathlib.Path(__file__).parent.absolute()/'seed.json') as in_file:
        data = json.load(in_file)

    return data
