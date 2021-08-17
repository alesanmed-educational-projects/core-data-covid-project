![header photo COVID](/assets/img/header.jpg!d)
# COVID Stuff
[![forthebadge made-with-python](assets/img/made-with-python.svg)](https://www.python.org/)

[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](/assets/img/built-with-sabrosura.svg)](https://forthebadge.com)


[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
![Built with Python](https://img.shields.io/pypi/pyversions/covid-data)
![Deploy Badge](https://github.com/alesanmed-educational-projects/core-data-covid-project/actions/workflows/okteto_deploy.yml/badge.svg)

Welcome to my Data project made in the context of [CORE School](https://www.corecode.school/).

This project is for loading, processing as well as showing several data related to COVID.

### You can play with the project [here](https://covid-data-alesanmed.cloud.okteto.net/)

# Table of contents

- [Splitting 💔](#splitting)
  - [COVID-data 🤖](#covid-data)
  - [COVID-backend 📡](#covid-backend)
  - [COVID-dashboard ✨](#covid-dashboard)
- [Local deployment 🔨🔧](#local-deployment)
  - [With Docker 🐳](#with-docker)
  - [From source ⛲](#from-source)
- [Dataset Used 📚](#data-used)
- [License](#license)

## División 💔 <a name="splitting"></a>

This project is composed of several pieces, each of them with its README. Those pieces are:

1. [covid-data](https://github.com/alesanmed-educational-projects/covid-data)
2. [flask-backend](backend)
3. [streamlit-dashboard](dashboard)

### COVID-data 🤖 <a name="covid-data"></a>

![CLI usage](/assets/img/CLI.png)

[covid-data](https://pypi.org/project/covid-data/) is a Python package in charge of loading and accessing the data. The backend uses it for retrieving data from the Database. The library holds all the SQL queries needed (so far) for accessing the data.

It can also be used as a CLI to load the data in an empty database.

### COVID-backend 📡 <a name="covid-backend"></a>

![Postman API request](/assets/img/API_req.png)

The backend is made with Flask, exposing several endpoints to serve country and COVID cases data.

This backend serves all the necessary data to the Dashboard.

### COVID-dashboard ✨ <a name="covid-dashboard"></a>

![Dashboard image](/assets/img/dashboard.png)

Last but not least, the frontend is a Streamlit application with different plots to explore and visualize the data.

This application presents an interactive panel to the user. The data shown is asked to the backend.

## Despliegue local 🔨🔧 <a name="local-deployment"></a>

### En Docker 🐳 <a name="with-docker"></a>

To deploy this project using Docker, you only have to clone the repository and bring it up with docker-compose.

```
git clone https://github.com/alesanmed-educational-projects/core-data-covid-project.git

cd core-data-covid-project

docker-compose up
```

### From source ⛲ <a name="from-source"></a>

[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/alesanmed-educational-projects/core-data-covid-project)


If you want to take this path, I recommend:
 1. Clone the repository
 2. Open it in your favorite IDE
 3. Follow the steps in each part's README

## Dataset used 📚 <a name="data-used"></a>

I got the base data from [Time Series Data Covid-19 Global](https://www.kaggle.com/baguspurnama/covid-confirmed-global) dataset.

These data go from January 2020 until July 2021. For extending the information with more recent data (from Spain and France), I used the following data sources:

- Spain: [Centro Nacional de Epidemiología](https://cnecovid.isciii.es/)
- France: [Plateforme ouverte des données publiques françaises](https://www.data.gouv.fr/fr/)

For enhancing the data with normalized locations, I used [OpenCageData](https://opencagedata.com/)

## License

[The Unlicense](LICENSE)
