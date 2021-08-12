import json
import logging
import os
from datetime import datetime

import click
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from covid_data.db import close_db, get_db
from covid_data.db.queries import create_case
from covid_data.logger import init_logger
from covid_data.types import CaseType, OnConflictStrategy
from covid_data.utils.places import create_country, create_province
from psycopg2._psycopg import connection  # pylint: disable=no-name-in-module

logger = logging.getLogger("covid-data")

START_DATE = datetime(2020, 3, 2)


def scrap_cases(engine: connection, start_date: datetime = START_DATE) -> None:
    URL = "https://cnecovid.isciii.es/covid19/#ccaa"

    page = requests.get(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/51.0.2704.103 Safari/537.36"
            )
        },
    )

    if page.status_code > 399:
        message = f"Error fetching cases in {__file__} scrapper"
        logger.error(message)
        raise click.ClickException("Empty CCAA info")

    raw_response = page.content.decode("utf-8")
    html = BeautifulSoup(raw_response, features="html.parser")

    div_curve = html.find("div", id="curva-epidémica")

    if div_curve is None:
        message = "No data found in page"
        logger.error(message)
        click.echo(message)
        return None

    script_data = div_curve.find("script")

    if type(script_data) is not Tag:
        message = "No data found in page"
        logger.error(message)
        click.echo(message)
        return None

    json_data = json.loads(script_data.string or "{}")

    ccaa = [
        button["label"]
        for button in json_data["x"]["layout"]["updatemenus"][0]["buttons"]
    ]

    for i, ca in enumerate(ccaa):
        message = f"Fetching cases for province {i + 1}/{len(ccaa)}"
        logger.info(message)
        click.echo(message)
        data_element = json_data["x"]["data"][i]

        cases = zip(data_element["x"], data_element["y"])

        if i == 0:
            created_place = create_country(ca, engine)
        else:
            created_place = create_province(ca, engine, None, f"{ca}, Spain")

        for idx, case in enumerate(cases):
            logger.debug(f"Creating case {idx + 1}")
            date_str = case[0]

            date = datetime.strptime(date_str, "%Y-%m-%d")

            if date <= start_date:
                continue

            case_data = {
                "type": CaseType.CONFIRMED.value,
                "amount": case[1],
                "date": date,
                "country_id": created_place.country_id,
                "province_id": created_place.province_id,
                "county_id": None,
            }

            create_case(case_data, engine, OnConflictStrategy.REPLACE)


def scrap():
    pass


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    init_logger(
        os.path.join(os.path.dirname(__file__), "../../logs/covid_data.log"),
        logging.INFO,
    )
    engine = get_db()

    try:
        scrap_cases(engine, datetime(2020, 1, 1))
    except Exception as e:
        raise e
    finally:
        close_db(engine)
