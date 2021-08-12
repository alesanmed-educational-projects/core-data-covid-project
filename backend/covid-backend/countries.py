import json

from covid_data.db.queries import get_all_countries, get_provinces_by_country
from flask import Blueprint, request
from flask.wrappers import Response

from .db import get_db
from .utils import serialize_json

bp = Blueprint("countries", __name__, url_prefix="/countries")


@bp.route("/", methods=["GET"])
def get_countries():
    db = get_db()

    name = request.args.get("name", None)

    near = request.args.get("near", None)
    near_fixed = []

    if near:
        try:
            near_fixed = [float(p) for p in near.split(",")]

            if len(near_fixed) != 2:
                raise ValueError()

        except ValueError:
            raise ValueError(f"Lat long field {near} not valid")

    contries = get_all_countries(db, name, near_fixed)

    return Response(
        json.dumps(contries, default=serialize_json),
        200,
        {"content-type": "application/json"},
    )


@bp.route("/<int:country_id>/provinces", methods=["GET"])
def get_provinces(country_id: int):
    db = get_db()

    provinces = get_provinces_by_country(db, country_id)

    return Response(
        json.dumps(provinces, default=serialize_json),
        200,
        {"content-type": "application/json"},
    )
