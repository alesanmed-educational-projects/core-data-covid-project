from covid_data.db import get_db
from psycopg2._psycopg import connection, cursor  # pylint: disable=no-name-in-module


def fix_wrong_locations(engine: connection):
    countries_to_fix = [
        {
            "query": "alpha2='CA'",
            "update": "location=ST_SetSRID(ST_MakePoint(-106.346771, 56.130366), 4326)",
        }
    ]

    provinces_to_fix = [
        {
            "query": "name='Canarias'",
            "update": "code='CN'",
        },
        {"query": "name='Comunidad Foral De Navarra'", "update": "code='NC'"},
    ]

    with engine.cursor() as cur:
        cur: cursor

        for country_to_fix in countries_to_fix:
            cur.execute(
                f"UPDATE countries SET {country_to_fix['update']} WHERE {country_to_fix['query']}"  # nosec
            )

        for province_to_fix in provinces_to_fix:
            cur.execute(
                f"UPDATE provinces SET {province_to_fix['update']} WHERE {province_to_fix['query']}"  # nosec
            )


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    engine = get_db()

    try:
        fix_wrong_locations(engine)
    finally:
        engine.close()
