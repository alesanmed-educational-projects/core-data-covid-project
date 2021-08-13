import os
from typing import Callable

from psycopg2 import connect
from psycopg2._psycopg import connection  # pylint: disable=no-name-in-module

from .queries import create_case, create_country, create_county, create_province


def get_db(
    user: str = None,
    passwd: str = None,
    host: str = None,
    port: str = None,
    db: str = None,
) -> connection:
    return connect(
        (
            f"postgresql://{user or os.environ.get('POSTGRES_USER', '')}"
            f":{passwd or os.environ.get('POSTGRES_PASS', '')}@"
            f"{host or os.environ.get('POSTGRES_HOST', 'localhost')}"
            f":{port or os.environ.get('POSTGRES_PORT', '5432')}/"
            f"{db or os.environ.get('POSTGRES_DB', '')}"
        )
    )


def close_db(conn: connection) -> Callable:
    return lambda *args, **kwargs: conn.close()


__all__ = [
    "get_db",
    "create_case",
    "create_country",
    "create_province",
    "create_county",
]
