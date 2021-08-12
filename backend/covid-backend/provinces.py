import json

from covid_data.db.queries import get_all_provinces
from flask import Blueprint
from flask.wrappers import Response

from .db import get_db
from .utils import serialize_json

bp = Blueprint("provinces", __name__, url_prefix="/provinces")


@bp.route("/", methods=["GET"])
def get_provinces():
    db = get_db()

    contries = get_all_provinces(db)

    return Response(
        json.dumps(contries, default=serialize_json),
        200,
        {"content-type": "application/json"},
    )
