import os


class Config(object):
    BACK_URL: str = os.environ.get("BACK_URL", "")
