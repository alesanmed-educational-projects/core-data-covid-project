from covid_data.db import get_db as db
from covid_data.types import connection
from flask import Flask, current_app, g


def get_db():
    if "db" not in g:
        g.db = db(
            current_app.config["PG_USER"],
            current_app.config["PG_PASS"],
            current_app.config["PG_HOST"],
            current_app.config["PG_PORT"],
            current_app.config["PG_DB"],
        )

    return g.db


def close_db(_=None):
    conn: connection = g.pop("db", None)

    if conn is not None:
        conn.close()


def init_app(app: Flask):
    app.teardown_appcontext(close_db)  # type: ignore
