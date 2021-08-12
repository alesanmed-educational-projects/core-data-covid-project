import json
from http import HTTPStatus
from logging import getLogger

from covid_data.db.queries import (
    create_country,
    get_all_countries,
    get_provinces_by_country,
)
from flask import Blueprint, request
from flask.wrappers import Response
from werkzeug import exceptions

from .auth import authenticated
from .db import get_db
from .utils import serialize_json

bp = Blueprint("countries", __name__, url_prefix="/countries")


@bp.route("", methods=["GET"])
def get_countries():
    db = get_db()

    name = request.args.get("name", None)

    near = request.args.get("near", None)
    near_fixed = []

    if near:
        try:
            near_fixed = [float(p) for p in near.split(",")]

            if len(near_fixed) != 2:
                raise exceptions.BadRequest()

        except exceptions.BadRequest:
            raise exceptions.BadRequest(f"Lat long field {near} not valid")

    contries = get_all_countries(db, name, near_fixed)

    return Response(
        json.dumps(contries, default=serialize_json),
        HTTPStatus.OK,
        {"content-type": "application/json"},
    )


@bp.route("", methods=["POST"])
@authenticated
def add_country():
    logger = getLogger("covid-backend")

    db = get_db()

    country_data = request.json or {}

    try:
        inserted_id = create_country(country_data, db)
    except Exception as e:
        logger.error("Error creating country")
        logger.error(e)
        raise exceptions.BadRequest("Invalid country")

    return Response(
        json.dumps({"id": inserted_id}, default=serialize_json),
        HTTPStatus.CREATED,
        {"content-type": "application/json"},
    )


@bp.route("/<int:country_id>/provinces", methods=["GET"])
def get_provinces(country_id: int):
    db = get_db()

    provinces = get_provinces_by_country(db, country_id)

    return Response(
        json.dumps(provinces, default=serialize_json),
        HTTPStatus.OK,
        {"content-type": "application/json"},
    )
