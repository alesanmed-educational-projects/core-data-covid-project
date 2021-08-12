import os

from flask import Blueprint
from flask import current_app as app
from flask import request
from flask.wrappers import Response
from werkzeug import FileStorage, secure_filename

bp = Blueprint("email", __name__, url_prefix="/email")


def allowed_file(filename: str):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@bp.route("/", methods=["POST"])
def send_email_pdf():
    if "file" not in request.files:
        raise ValueError("No file sent")

    file: FileStorage = request.files["file"]

    if file and allowed_file(file.filename or ""):
        filename = secure_filename(file.filename or "")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    else:
        raise ValueError("The file sent is not valid")

    return Response(status=201)
