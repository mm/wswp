"""Stores Flask configuration variables.
"""

import os


class Config(object):
    """Base configuration all others inherit from.
    """
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_OFF = bool(int(os.getenv('ADMIN_OFF', 0)))


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TEST = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "postgresql://wswp:supersecure@localhost:5433/wswp_test")
