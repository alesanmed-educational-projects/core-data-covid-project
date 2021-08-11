import json

from covid_data.db.queries import get_all_countries
from flask import Blueprint
from flask.wrappers import Response

from .db import get_db
from .utils import serialize_json

bp = Blueprint("countries", __name__, url_prefix="/countries")


@bp.route("/", methods=["GET"])
def get_countries():
    db = get_db()

    contries = get_all_countries(db)

    return Response(
        json.dumps(contries, default=serialize_json),
        200,
        {"content-type": "application/json"},
    )
