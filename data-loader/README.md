# Data Loader

Este proyecto contiene las herramientas necesarias para:
- Crear la base de datos
- Cargar datos en esa base de datos
- Consultar esos datos

Este proyecto se puede usar de 2 formas.

## Como CLI


Para cargar los datos se puede usar como CLI. Lo primero será crear la base de datos con el esquema disponible en [a relative link](covid_data/db/schema/db_schema.sql). La estructura de la base de datos es la siguiente:

![Database ERD](assets/img/erd-covid.png)

Una vez está creada la base de datos, se pueden cargar los datos de los archivos CSV con el siguiente comando:

```bash
python covid_data/app.py loadcsv /path/to/confirmed.csv,/path/to/dead.csv,/path/to/recovered.csv -tf -o
```

Para obtener ayuda sobre cómo usar el comando, ejecuta:

```bash
❯ python covid_data/app.py --help
Usage: app.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  loadcsv  Loads FILES as CSV data.
  scrap    Scrap cases of chosen COUNTRY.
```

Hay 2 comandos disponibles

### loadcsv

```bash
❯ python covid_data/app.py loadcsv --help
Usage: app.py loadcsv [OPTIONS] FILES

  Loads FILES as CSV data. If you want to load several files, each file should
  be separated by comma

Options:
  -t, --type TEXT      Type of cases contained in each file, separated by
                       comma. Leave blank if using --type-in-file
  -tf, --type-in-file  Set this to true if the file names are <case_type>.csv
                       Being <case_type> one of confirmed, recovered or dead
  -o, --optimize       Set to true to skip lines for places that has more
                       cases than columns on the CSV
  --help               Show this message and exit.
```

Este comando te permite procesar y cargar en la base de datos uno o más archivos CSV. Cada archivo debe contener información de un solo tipo de casos.

Las rutas a los archivos deben ir separados por comas.

De igual manera, el tipo de caso de cada archivo debe ir separados por comas en el argumento `--type` y **en el mismo orden** que los archivos.

Otra opción es no usar el argumento `--type` y nombrar los archivos con el tipo de caso que contienten, e.g. `recovered.csv`. Si se toma esta alternativa, se debe usar el parámetro `--type-in-file`.

Por último, el argumento `--optimize` se saltará todas las filas en las que el país al que hacen referencia ya tenga el mismo (o más) número de casos del tipo del archivo, que columnas tiene el CSV.

Un ejemplo de uso de este comando para cargar los CSVs con todos los datos es:

```bash
python covid_data/app.py loadcsv /path/to/confirmed.csv,/path/to/dead.csv,/path/to/recovered.csv -tf -o
```

Usa el nombre del archivo para nombrar el tipo de caso y la optimización.

### scrap

Este comando permite hacer scrapping de un país concreto. Se usa para ampliar datos por país.

El uso de este comando se detalla aquí:

```bash
Usage: app.py scrap [OPTIONS] COUNTRY

  Scrap cases of chosen COUNTRY. To check available countries to scrap use
  --check

Options:
  --check            Use this to check available countries
  --start-date TEXT  Date to start scraping cases from, in format DD/MM/YYYY
  --help             Show this message and exit.
``` 

Hay un argumento que es obligatorio y es el país a scrappear. Si se quiere saber qué países hay disponibles, basta con poner cualquier valor en `COUNTRY` y pasar el parámetro `--check`:

```bash
❯ python covid_data/app.py scrap XXX --check
Available countries are:
        France
        Spain
```

Y, una vez se sabe qué país se va a usar, se lanza el scrapper:

```bash
❯ python covid_data/app.py scrap spain
Fetching cases for province 1/20
Fetching cases for province 2/20
Fetching cases for province 3/20
...
```

Se puede especificar la fecha de inicio usando el argumento `--start-date`. La fecha debe estar en formato `DD/MM/YYYY`

```bash
python covid_data/app.py scrap France --start-date 01/08/2021
```

### **Añadir nuevos scrappers**

Añadir un nuevo scrapper para un país es tan sencillo como colocar un archivo `<country_name>.py` en la carpeta `scrappers` y que ese archivo exponga una función:

```python
def scrap(db_engine: psycopg2._psycopg.connection, start_date: datetime.datetime)
```

## Como biblioteca

La parte más interesante de este paquete como biblioteca es el sumbódulo de queries, qeu se detalla a continuación.

### Glossary
- `connection: psycopg2._psycopg.connection`
- `CaseType: covid_data.types.CaseType`
- `Aggregations: covid_data.types.Aggregations`
- `CaseType: covid_data.types.CaseType`
- `OnConflictStrategy: covid_data.types.OnConflictStrategy`
- `OrderBy: covid_data.types.OrderBy`
- `PlaceProperty: covid_data.types.PlaceProperty`
- `PlaceTable: covid_data.types.PlaceTable`
- `PlaceType: covid_data.types.PlaceType`



```python
def place_exists(
    place: str, engine: connection, table: PlaceTable = PlaceTable.COUNTRY
) -> Union[str, None]:
"""Given a place name and a table, returns its ID or none if not exits"""
```

```python
def get_country_by_alpha2(country: str, engine: connection) -> Optional[dict]:
"""Given an alpha2 code, return a country"""
```

```python
def get_country_by_alpha3(country: str, engine: connection) -> Optional[dict]:
"""Given an alpha3 code, return a country"""
```

```python
def get_province_by_alpha2(province: str, engine: connection) -> Optional[dict]:
"""Given an alpha2 code, return a province"""
```

```python
def get_county_by_alpha2(county: str, engine: connection) -> Optional[dict]:
"""Given an alpha2 code, return a county"""
```

```python
def get_country_by_id(country_id: str, engine: connection) -> Optional[dict]:
"""Given an id, return a country"""
```

```python
def get_province_by_id(province_id: str, engine: connection) -> Optional[dict]:
"""Given an id, return a province"""
```

```python
def get_province_by_name(province: str, engine: connection) -> Optional[dict]:
"""Given a name, return a country"""
```

```python
def get_county_by_id(county_id: str, engine: connection) -> Optional[dict]:
"""Given an id, return a county"""
```

```python
def row_to_dict(
    rows: Iterable, table_or_cols: Union[str, Iterable[str]], engine: connection
) -> list[dict]:
"""Given an array of rows and a table or a column lists, transform the rows to an array of dicts, with columns as keys"""
```

```python
def ensure_array(element) -> List:
"""Given an object, ensure it's an array"""
```

```python
def create_country(country: dict, engine: connection) -> str:
"""Given a dict with all country data, insert it in the database"""
```

```python
def create_province(province: dict, engine: connection) -> str:
"""Given a dict with all province data, insert it in the database"""
```

```python
def create_county(county: dict, engine: connection) -> str:
"""Given a dict with all county data, insert it in the database"""
```

```python
def get_cases_by_country(
    country_id: int, engine: connection, case_type: CaseType = None
) -> List[Dict]:
"""Given a dict with all country data, insert it in the database"""
```

```python
def get_cases_by_province(
    province_id: int, engine: connection, case_type: CaseType = None
) -> List[Dict]:
"""Given a province id, return all the cases from that provicen, filtered by type if provided"""
```

```python
def get_cases_by_filters_query(
    country_id: int = None,
    province_id: int = None,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    aggregation: list[Aggregations] = [],
    limit: int = None,
    sort: list[str] = [],
) -> Dict[str, Any]:
"""
Returns a query that matches all the filters passed. The returned query is splitted so that the caller can manipulate it before executing. The return dict is in the form:

{
    "select": select,
    "from": from_,
    "query": query,
    "params": tuple(params),
    "columns": tuple(columns),
}
"""
```

```python
def get_cum_cases_by_date(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
) -> List[Dict]:
"""
Returns the cummulative sum of cases aggregated by date. Filtered by date and type if provided
"""
```

```python
def get_cum_cases_by_date_country(
    engine: connection,
    country_id: int,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
) -> List[Dict]:
"""
Returns the cummulative sum of cases aggregated by date and contry. Filtered by date and type if provided
"""
```

```python
def get_cum_cases_by_country(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
) -> List[Dict]:
"""
Returns the cummulative sum of cases aggregated by country. Filtered by date and type if provided
"""
```

```python
def get_cum_cases_by_province(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    country_id: int = None,
) -> List[Dict]:
"""
Returns the cummulative sum of cases aggregated by province. Filtered by date and type if provided
"""
```

```python
def create_case(
    case: dict,
    engine: connection,
    conflict_strategy: OnConflictStrategy = OnConflictStrategy.REPLACE,
) -> bool:
"""
Given all the data regarding a case, create it. Also takes a replace strategy that can be set to replace or upsert.
"""
```

```python
def get_all_countries(
    engine: connection, name: str = None, near: list[float] = []
) -> list[dict]:
"""
Get all countries filtered by name if provided and ordered by distance to `near`
"""
```

```python
def get_all_provinces(engine: connection) -> list[dict]:
"""
Get all provinces
"""
```

```python
def get_provinces_by_country(engine: connection, country_id: int) -> list[dict]:
"""
Get all provinces that belongs to a specific country
"""
```

```python
def insert_api_key(engine: connection, hashed_key: str) -> bool:
"""
Creates an api key
"""
```

```python
def check_api_key(engine: connection, hashed_key: str) -> bool:
"""
Check if the incoming key exists
"""
```
