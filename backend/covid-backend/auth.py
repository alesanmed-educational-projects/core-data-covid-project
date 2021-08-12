import functools
import hashlib
import secrets
from http import HTTPStatus
from logging import getLogger

import click
from covid_data.db import get_db
from covid_data.db.queries import check_api_key, insert_api_key
from flask import request
from flask.app import Flask
from flask.blueprints import Blueprint
from flask.cli import with_appcontext
from flask.wrappers import Response
from werkzeug import exceptions


@click.command("create-api-key")
@with_appcontext
def create_api_key():
    logger = getLogger("covid-backend")
    db = get_db()

    api_key = secrets.token_urlsafe(32)
    logger.info(api_key)

    hashed_key = hashlib.sha256(api_key.encode("utf-8"))

    insert_api_key(db, hashed_key.hexdigest())


def init_app(app: Flask):
    cli: click.Group = app.cli

    cli.add_command(create_api_key)


def authenticated(endpoint):
    @functools.wraps(endpoint)
    def wrapped_endpoint(**kwargs):
        db = get_db()

        auth_header = request.headers.get("Authorization", "").split(" ")

        if not len(auth_header) == 2:
            raise exceptions.Unauthorized("Unauthorized")

        key: str = auth_header[1]

        success = check_api_key(db, hashlib.sha256(key.encode("utf-8")).hexdigest())

        if not success:
            raise exceptions.Unauthorized("Unauthorized")

        return endpoint(**kwargs)

    return wrapped_endpoint


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("", methods=["POST"])
@authenticated
def auth():
    return Response(status=HTTPStatus.OK)
