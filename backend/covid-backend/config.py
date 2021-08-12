import os


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    PG_USER = os.environ.get("PG_USER", "")
    PG_PASS = os.environ.get("PG_PASS", "")
    PG_HOST = os.environ.get("PG_HOST", "")
    PG_PORT = os.environ.get("PG_PORT", "")
    PG_DB = os.environ.get("PG_DB", "")
    SENDGRID_KEY = os.environ.get("SENDGRID_KEY", "")


class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
