![cabecera foto COVID](/assets/img/header.jpg!d)
# Las cositas del COVID
[![forthebadge made-with-python](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](/assets/img/built-with-sabrosura.svg)](https://forthebadge.com)


[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
![Built with Python](https://img.shields.io/pypi/pyversions/covid-data)
![Deploy Badge](https://github.com/alesanmed-educational-projects/core-data-covid-project/actions/workflows/okteto_deploy.yml/badge.svg)

Bienvenido a mi proyecto de data del bootcamp de [CORE](https://www.corecode.school/).

Este proyecto intenta cargar, procesar y mostrar ciertos datos relacionados con la COVID.

# Table of contents

- [Las cositas del COVID](#las-cositas-del-covid)
  - [División 💔](#division)
    - [COVID-data 🤖](#covid-data)
    - [COVID-backend 📡](#covid-backend)
    - [COVID-dashboard ✨](#covid-dashboard)
  - [Despliegue local 🔨🔧](#despliegue-local)
    - [En Docker 🐳](#en-docker)
    - [A partir del código fuente ⛲](#a-partir-del-codigo-fuente)
  - [Datos usados 📚](#datos-usados)
  - [Licencia](#licencia)

## División 💔 <a name="division"></a>

Este proyecto consta de varias partes, cada una con su propio README específico. Estas piezas son:

1. `covid-data`
2. `flask-backend`
3. `streamlit-dashboard`

### COVID-data 🤖 <a name="covid-data"></a>

![CLI usage](/assets/img/CLI.png)

[covid-data](https://pypi.org/project/covid-data/) Es un paquete de Python que se encarga de toda la carga y acceso a los datos. Se usa como biblioteca en el backend para acceder a la base de datos almacenar todas las queries.

También se puede usar como CLI para cargar los datos en una base de datos nueva.

### COVID-backend 📡 <a name="covid-backend"></a>

![Petición API en Postman](/assets/img/API_req.png)

El backend se compone de una aplicación en flask que expone una serie de endpoints para pedir datos de países y casos de COVID.

Este backend lo usa el dashboard para pedir todos los datos necesarios.

### COVID-dashboard ✨ <a name="covid-dashboard"></a>

![Dashboard image](/assets/img/dashboard.png)

Por último, el frontend es una aplicación de Streamlit en la que se muestran gráficas de exploración y visualización de datos.

Este frontend pide los datos al backend en flask y los vuelca en un panel interactivo.

## Despliegue local 🔨🔧 <a name="despliegue-local"></a>

### En Docker 🐳 <a name="en-docker"></a>

Para desplegar este proyecto en Docker es tan sencillo como clonarte el código del proyecto y levantarlo con docker-compose.

```
git clone https://github.com/alesanmed-educational-projects/core-data-covid-project.git

cd core-data-covid-project

docker-compose up
```

### A partir del código fuente ⛲ <a name="a-partir-del-codigo-fuente"></a>

[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/alesanmed-educational-projects/core-data-covid-project)


Para eso te recomiendo que abras el proyecto con tu IDE favorito y sigas las instrucciones del README de cada pieza.

## Datos usados 📚 <a name="datos-usados"></a>

Se ha partido del Dataset [Time Series Data Covid-19 Global](https://www.kaggle.com/baguspurnama/covid-confirmed-global).

Estos datos comprenden desde el enero de 2020 a julio de 2021. Para ampliar los datos con información más reciente (en España y Francia) se han usado datos obtenidos de:

- España: [Centro Nacional de Epidemiología](https://cnecovid.isciii.es/)
- Francia: [Plateforme ouverte des données publiques françaises](https://www.data.gouv.fr/fr/)

Para enriquecer los datos y completar y normalizar las localizaciones, se ha usado [OpenCageData](https://opencagedata.com/)

## Licencia

[The Unlicense](LICENSE)
