''' 
Configuration file
This file contains different  configurations of our application in the development mode and the Production mode.
It mainly contains the database credentials.

'''
from importlib.metadata import files
import os
import secrets
secret = secrets.token_urlsafe(32)


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = secret

    DB_NAME = os.environ.get("DB_NAME")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    SESSION_COOKIE_SECURE = True


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True

    DB_NAME = os.environ.get("DB_NAME")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    SECRET_KEY = secret
    SESSION_COOKIE_SECURE = False
