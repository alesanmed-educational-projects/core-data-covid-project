import os
from contextlib import ExitStack
from datetime import datetime
from logging import getLogger

import click
import pandas as pd
from click.exceptions import ClickException
from covid_data.db import close_db, get_db
from covid_data.db.queries import (
    create_case,
    get_cases_by_country,
    get_cases_by_province,
)
from covid_data.errors import (
    PlaceInfoFetchException,
    PlaceInfoNotCompleteException,
    PlaceNameNotProvidedException,
    PlaceNotMatchedException,
)
from covid_data.types import CaseType, OnConflictStrategy
from covid_data.utils.places import CreatedPlace, create_country, create_province

logger = getLogger("covid-data")


def insert_data(df: pd.DataFrame, case_type: CaseType, optimize: bool = True) -> None:
    with ExitStack() as stack:
        engine = get_db()

        stack.push(close_db(engine))

        num_rows = df.shape[0]

        for index, row in enumerate(df.itertuples(index=False)):
            message = f"Processing row {index + 1}/{num_rows}"
            logger.info(message)
            click.echo(message)
            state: str = row[df.columns.get_loc("Province/State")]
            country: str = row[df.columns.get_loc("Country/Region")]
            lat: float = row.Lat
            lng: float = row.Long
            created_country = CreatedPlace()
            created_province = CreatedPlace()

            if (pd.isna(lat) or pd.isna(lng)) or (lat == 0 or lng == 0):
                message = f"Skipping line {index + 2} due to missing location"
                logger.warning(message)
                click.echo(message)
                continue

            err = False
            try:
                if not pd.isna(state):
                    created_province = create_province(state.replace("*", ""), engine)

                if not pd.isna(country):
                    created_country = create_country(country.replace("*", ""), engine)
            except PlaceInfoFetchException:
                err = True
                message = f"Skipping line {index + 2}"
                logger.error(message)
                click.echo(message)
            except (PlaceInfoNotCompleteException, PlaceNotMatchedException):
                err = True
                message = f"Skipping line {index + 2} due to incomplete information in fetching"
                logger.error(message)
                click.echo(message)
            except PlaceNameNotProvidedException:
                err = True
                message = f"Skipping line {index + 2} because no place name could be extracted"
                logger.error(message)
                click.echo(message)
            except (TypeError, KeyError) as e:
                err = True
                message = (
                    f"Skipping line {index + 2} due to missing information in fetching"
                )
                logger.error(e)
                click.echo(e)
                logger.error(message)
                click.echo(message)

            if err:
                continue

            cols = df.columns.drop(["Province/State", "Country/Region", "Lat", "Long"])

            num_columns = len(cols)

            saved_cases = []

            if created_province.province_id and created_country.country_id:
                saved_cases = get_cases_by_province(
                    int(created_province.province_id),
                    engine,
                    case_type,
                )
            elif created_country.country_id:
                saved_cases = get_cases_by_country(
                    int(created_country.country_id), engine, case_type
                )

            if optimize and len(saved_cases) >= num_columns:
                message = f"Skipping line {index + 2} for optimizations"
                logger.debug(message)
                click.echo(message)
                continue

            for i, date_str in enumerate(cols):
                message = f"Processing case {i+1}/{num_columns}"
                logger.debug(message)
                click.echo(message)
                date_padded: str

                date_padded = "/".join([part.zfill(2) for part in date_str.split("/")])

                date = datetime.strptime(date_padded, "%m/%d/%y")

                case = {
                    "type": case_type.value,
                    "amount": row[df.columns.get_loc(date_str)],
                    "date": date,
                    "country_id": created_country.country_id,
                    "province_id": created_province.province_id,
                    "county_id": None,
                }

                create_case(case, engine, OnConflictStrategy.REPLACE)


@click.command("loadcsv")
@click.argument("files")
@click.option(
    "-t",
    "--type",
    default="",
    help="Type of cases contained in each file, separated by comma. Leave blank if using --type-in-file",
)
@click.option(
    "-tf",
    "--type-in-file",
    default=True,
    help="Set this to true if the file names are <case_type>.csv Being <case_type> one of confirmed, recovered or dead",
    is_flag=True,
)
@click.option(
    "-o",
    "--optimize",
    default=True,
    help="Set to true to skip lines for places that has more cases than columns on the CSV",
    is_flag=True,
)
def main(files: str, type: str = "", type_in_file: bool = True, optimize: bool = True):
    """Loads FILES as CSV data. If you want to load several files, each file should be separated by comma"""
    file_paths = files.split(",")

    types_fix = []
    types = []

    if not type_in_file:
        types = type.split(",")
    else:
        for file_path in file_paths:
            file_type = os.path.basename(file_path).replace(".csv", "")
            types.append(file_type)

    for type in types:
        if type not in {t.value for t in CaseType.__members__.values()}:
            raise ClickException("Type {type} not valid")
        types_fix.append(CaseType(type))

    for info in zip(file_paths, types_fix):
        message = f"Inserting {info[1]} cases"
        logger.info(message)
        click.echo(message)

        path: str = info[0]

        df = pd.read_csv(path)

        insert_data(df, info[1], optimize)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
