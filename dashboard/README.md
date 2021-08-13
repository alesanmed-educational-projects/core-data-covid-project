# Streamlit dashboard

Este proyecto contiene el cuadro de mandos. Hecho en streamlit.

## Ejecución

Para poder ejecutar este dashboard lo primero es descargar el código. Luego se puede ejecutar con Docker o sin él.

### Docker

Símplemente levantar el docker-compose:

```
docker-compose up --build
```

### Local

Primero hay que instalar las dependencias con:

```
pip install -r requirements.txt
```

O, si usas [Poetry](https://python-poetry.org/):

```
poetry install
```

Una vez las dependencias están instaladas, puedes ejecutar dashboard:

```
streamlit run app/main.py
```

## Configuración

El proyecto se vale de las siguientes variables de entorno para su configuración:

- BACK_URL: URL de la API de flask

## General data

Contiene datos generales del coronavirus. Casos globales, gráficas globlales y por países y un mapa.

Se pueden filtrar los datos por países y por tipos, además de elegir el tipo de gráfica.

## Country data

Contiene datos detallados por país. Se desglosan por provincias y se puede exportar a PDF y mandar ese PDF por email.

De nuevo, se puede filtrar por provincias, tipo de caso y tipo de gráfica.

## Manage data

Permite crear países nuevos usando un API key. Los países creados deberán estar disponibles inmediatamente.
