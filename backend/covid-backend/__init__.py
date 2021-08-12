import os
import sys

from dotenv import load_dotenv
from flask import Flask

from .logger import init_logger, log_uncaught_exception

load_dotenv()


def create_app(test_config=None):
    sys.excepthook = log_uncaught_exception

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")
    app.url_map.strict_slashes = False

    init_logger(os.path.join(os.path.dirname(__file__), "../logs/backend.log"))

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object("covid-backend.config.Config")
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "../tmp")
    app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import cases

    app.register_blueprint(cases.bp)

    from . import countries

    app.register_blueprint(countries.bp)

    from . import provinces

    app.register_blueprint(provinces.bp)

    from . import email

    app.register_blueprint(email.bp)

    from . import auth

    auth.init_app(app)

    app.register_blueprint(auth.bp)

    from . import errors

    app.register_blueprint(errors.bp)

    return app
