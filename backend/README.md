# Backend

Este proyecto contiene el backend de la aplicación. Aquí es donde ocurre toda la magia.

Este proyecto usa el paquete de covid-data para acceder a las queries.

Los endpoints que expone esta API son:

`POST /auth`

Authorization: Bearer token. Comprueba si una API key es válida

`GET /cases`

Devuelve casos acorde a una serie de filtros opcionales. A saber:

- `type`: Tipo de caso. Válidos `recovered`, `confirmed`, `dead`
- `agg`: Campos por los que aggregar. Válidos `date`, `country`, `type`, `province`, `province_code`
- `resultType`: Tipo de acumulación que se quiere. Válidos `cummulativeDate`, `cummulativeDateCountry`, `cummulativeCountry`, `cummulativeProvince`
- `country`: País por el que filtrar
- `province`: Provincia por la que filtrar
- `date`: Fecha exacta para filtrar
- `date[gte]`: Fecha límite por debajo para pedir datos
- `date[lte]`: Fecha límite por arriba para pedir datos
- `limit`: Máximo número de registros que devolver
- `sort`: Campos por los que filtrar, en la forma `[field, -other]`
- `normalize`: Si devolver la columna `amount` normalizada

`GET /countries`

Devuelve los países acorde a una serie de filtros opcionales. A saber:

- `name`: Nombre del país
- `near`: Latitud y longitud, separadas por comas. Los resultados saldrán ordenados acorde a la distancia del país a ese punto.

`POST /countries`

Crea un país con los datos pasados en el cuerpo. El formato es JSON y todos los campos son obligatorios:

```json
{
    "name": "Pais",
    "alpha2": "PS",
    "alpha3": "PAS",
    "lat": "37.401875",
    "lng": "-5.9890039"
}
```

`GET /countries/:id/provinces`

Devuelve las provincias que pertenencen al país con la ID indicada

`POST /email`

Envía un email con el PDF enviado en el POST. Debe ser un `form-data` con el PDF en `files` y el email del receptor en `recipient`.

`GET /provinces`
Devuelve todas las provincias

## Crear una API Key

Para poder crear un país hace falta mandar una API Key en las cabeceras. Para generar esta clave se debe ejecutar el comando:

```
FLASK_APP=covid-backend flask create-api-key
```

La API Key creada aparecerá en la consola.
