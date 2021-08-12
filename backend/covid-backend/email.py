import base64
import json
import logging
import re

import requests
from flask import Blueprint
from flask import current_app as app
from flask import request
from flask.wrappers import Response
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .errors import FailedDependencyError

bp = Blueprint("email", __name__, url_prefix="/email")

SENDGRID_URL = "https://sendgrid.com/v3"


def allowed_file(filename: str):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@bp.route("", methods=["POST"])
def send_email_pdf():
    logger = logging.getLogger("covid-backend")

    if "file" not in request.files:
        raise ValueError("No file sent")

    file: FileStorage = request.files["file"]

    body = request.form

    email_to = body.get("recipient", "")

    email_regex = r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+"

    if not email_to or not re.match(email_regex, email_to):
        raise ValueError("Recipient email is no valid")

    if file and allowed_file(file.filename or ""):
        filename = secure_filename(file.filename or "")
    else:
        raise ValueError("The file sent is not valid")

    file_bytes = file.stream.read()

    SENDGRID_FULL_URL = f"{SENDGRID_URL}/mail/send"

    request_body = {
        "personalizations": [{"to": [{"email": email_to}]}],
        "from": {"email": "alesanchezmedina@gmail.com", "name": "Ale Sanchez"},
        "subject": "La sabrosura llego!",
        "content": [
            {
                "type": "text/plain",
                "value": "El diverti-email llego a tu bandeja. Adjunto tienes el PDF :)",
            }
        ],
        "attachments": [
            {
                "content": base64.b64encode(file_bytes).decode("latin-1"),
                "type": "application/pdf",
                "filename": filename,
            }
        ],
    }

    email_response = requests.post(
        SENDGRID_FULL_URL,
        data=json.dumps(request_body),
        headers={
            "Authorization": f"Bearer {app.config['SENDGRID_KEY']}",
            "content-type": "application/json",
        },
    )

    if email_response.status_code > 399:
        logger.error(email_response.status_code)
        logger.error(email_response.text)
        raise FailedDependencyError("Unable to send email")

    return Response(status=201)
