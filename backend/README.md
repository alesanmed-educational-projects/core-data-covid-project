# COVID-backend
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

This part holds the application backend. Here's where the magic happens 🏀.

The backend relies on [covid-data](https://pypi.org/project/covid-data/) package to access the queries for managing and asking data to the database.

# Table of contents

- [Running the code 🚂](#running-code)
  - [Pre-requisites 🛒](#pre-reqs)
  - [Installation 🎢](#installing)
  - [Configuration ⚙](#configuring)
  - [Execution 🎯](#running)
- [Endpoints 🛎](#endpoints)
- [Creating an API key 🗝](#api-key)

## Running the code 🚂 <a name="running-code"></a>

If you want to run the backend from source, clone it and install the dependencies.

```
git clone https://github.com/alesanmed-educational-projects/core-data-covid-project.git

cd core-data-covid-project/backend
```

### Pre-requisites 🛒 <a name="pre-reqs"></a>

- [psycopg2](https://www.psycopg.org/install/)

### Installation 🎢 <a name="installing"></a>

First, install the dependencies using pip:

```
pip install -r requirements.txt
```

Or, if you use [Poetry](https://python-poetry.org/):

```
poetry install
```

### Configuration ⚙ <a name="configuring"></a>

The project looks for the following environment variables to configure several parts:

- POSTGRES_USER: Postgres username
- POSTGRES_PASS: Postgres password
- POSTGRES_HOST: Postgres host
- POSTGRES_PORT: Postgres port
- POSTGRES_DB: Postgres database
- SENDGRID_KEY: Sendgrid API key for sending emails

You can create a Sendgrid API key from their [website](https://sendgrid.com/).

### Execution 🎯 <a name="running"></a>

Once you have installed the dependencies, you can bring the server up:

```
FLASK_APP=covid-backend flask run
```

## Endpoints 🛎 <a name="endpoints"></a>

All info about the API endpoints and the parameters accepted are in [API.md](API.md)

## Creating an API key 🗝 <a name="api-key"></a>

To create a country, you have to send an API key in the request headers. To generate that API key, you can run the command:

```
FLASK_APP=covid-backend flask create-api-key
```

The newly created API Key will show up in the terminal. Also, you can find it saved in the database configured via env variables.
