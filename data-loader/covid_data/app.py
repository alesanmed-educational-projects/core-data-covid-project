import os
from importlib import import_module

import click
from covid_data.logger import init_logger
from dotenv import load_dotenv

load_dotenv()

init_logger(os.path.join(os.path.dirname(__file__), "../logs/covid_data.log"))


@click.group()
def cli():
    pass


if __name__ == "__main__":
    base_path = os.path.join(os.path.dirname(__file__), "commands")
    files = os.listdir(base_path)

    for file_name in files:
        if file_name.startswith("test"):
            continue

        handler_module, _ = os.path.splitext(file_name)

        module = import_module(f".{handler_module}", "commands")

        if not hasattr(module, "main"):
            continue

        cli.add_command(module.main)  # type: ignore

    cli()
