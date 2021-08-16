# COVID-backend
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

Este proyecto contiene el backend de la aplicación. Aquí es donde ocurre toda la magia.

En el backend se usa el paquete [covid-data](https://pypi.org/project/covid-data/) para acceder a las queries para manejar y pedir datos a la base de datos.

# Table of contents

- [Ejecución del código 🚂](#running-code)
  - [Pre-requisitos 🛒](#pre-reqs)
  - [Instalación 🎢](#installing)
  - [Configuración ⚙](#configuring)
  - [Ejecución 🎯](#running)
- [Endpoints 🛎](#endpoints)
- [Crear una API Key 🗝](#api-key)

## Ejecución del código 🚂 <a name="running-code"></a>

Para poder ejecutar el backend desde el código fuente es necesario, lo primero, clonar el código e instalar las dependencias.

```
git clone https://github.com/alesanmed-educational-projects/core-data-covid-project.git

cd core-data-covid-project/backend
```

### Pre-requisitos 🛒 <a name="pre-reqs"></a>

- [psycopg2](https://www.psycopg.org/install/)

### Instalación 🎢 <a name="installing"></a>

Primero hay que instalar las dependencias con:

```
pip install -r requirements.txt
```

O, si usas [Poetry](https://python-poetry.org/):

```
poetry install
```

### Configuración ⚙ <a name="configuring"></a>

El proyecto se vale de las siguientes variables de entorno para su configuración:

- POSTGRES_USER: Usuario de Postgres
- POSTGRES_PASS: Contraseña de Postgres
- POSTGRES_HOST: Host de Postgres
- POSTGRES_PORT: Puerto de Postgres
- POSTGRES_DB: Base de datos
- SENDGRID_KEY: API Key de Sendgrid para mandar emails

La clave API la puedes crear en la web de [Sendgrid](https://sendgrid.com/).

### Ejecución 🎯 <a name="running"></a>

Una vez las dependencias están instaladas, puedes ejecutar el servidor como tal:

```
FLASK_APP=covid-backend flask run
```

## Endpoints 🛎 <a name="endpoints"></a>

Toda la información de los endpoints que expone esta API y sus parámetros se encuentra en el archivo [API.md](API.md)

## Crear una API Key 🗝 <a name="api-key"></a>

Para poder crear un país hace falta mandar una API Key en las cabeceras. Para generar esta clave se debe ejecutar el comando:

```
FLASK_APP=covid-backend flask create-api-key
```

La API Key creada aparecerá en la consola y quedará guardada en la base de datos especificada en la configuración por variables de entorno
