import os
from contextlib import ExitStack
from datetime import datetime
from importlib import import_module
from typing import Any

import click
from covid_data.db import close_db, get_db


@click.command("scrap")
@click.argument("country")
@click.option(
    "--check", default=False, help="Use this to check available countries", is_flag=True
)
@click.option(
    "--start-date", help="Date to start scraping cases from, in format DD/MM/YYYY"
)
def main(country: str, check: bool = False, start_date: str = ""):
    """Scrap cases of chosen COUNTRY. To check available countries to scrap use --check"""
    with ExitStack() as stack:
        db = get_db()

        stack.push(close_db(db))

        base_path = os.path.join(os.path.dirname(__file__), "../scrappers")
        files = os.listdir(base_path)

        if check:
            click.echo("Available countries are:")

        for file_name in files:
            if file_name.startswith("test"):
                continue

            handler_module, _ = os.path.splitext(file_name)

            module = import_module(f".{handler_module}", "covid_data.scrappers")

            if not hasattr(module, "scrap"):
                continue

            if check:
                click.echo(f"\t{file_name.replace('.py', '').capitalize()}")
            elif handler_module == country.lower():
                args: list[Any] = [db]

                if start_date:
                    args.append(datetime.strptime(start_date, "%d/%m/%Y"))

                module.scrap(*args)  # type: ignore
