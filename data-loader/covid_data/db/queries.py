from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Union

from covid_data.types import (
    Aggregations,
    CaseType,
    OnConflictStrategy,
    OrderBy,
    PlaceProperty,
    PlaceTable,
    PlaceType,
)
from psycopg2 import sql
from psycopg2._psycopg import connection  # pylint: disable=no-name-in-module
from psycopg2._psycopg import cursor  # pylint: disable=no-name-in-module


def place_exists(
    place: str, engine: connection, table: PlaceTable = PlaceTable.COUNTRY
) -> Union[str, None]:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL("SELECT id FROM {0} WHERE name=%s").format(
                sql.Identifier(table.value)
            ),
            (place,),
        )

        result = cur.fetchone() or []

        if not len(result):
            return None
        else:
            return result[0]


def get_place_by_property(
    value: str, property: PlaceProperty, engine: connection, place_type: PlaceType
) -> Optional[dict]:
    from_table = None

    if place_type == PlaceType.COUNTRY:
        from_table = "countries"
    elif place_type == PlaceType.PROVINCE:
        from_table = "provinces"
    elif place_type == PlaceType.COUNTY:
        from_table = "counties"
    else:
        raise ValueError(f"Place type {place_type} not supported")

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL("SELECT * FROM {0} WHERE {1}=%s").format(
                sql.Identifier(from_table), sql.Identifier(property.value)
            ),
            (value,),
        )

        result = cur.fetchone() or []

        res = row_to_dict(result, from_table, engine)

        if not len(res):
            return None

        return res[0]


def get_country_by_alpha2(country: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        country, PlaceProperty.ALPHA_2_CODE, engine, PlaceType.COUNTRY
    )


def get_country_by_alpha3(country: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        country, PlaceProperty.ALPHA_3_CODE, engine, PlaceType.COUNTRY
    )


def get_province_by_alpha2(province: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        province, PlaceProperty.ALPHA_2_CODE, engine, PlaceType.PROVINCE
    )


def get_county_by_alpha2(county: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        county, PlaceProperty.ALPHA_2_CODE, engine, PlaceType.COUNTY
    )


def get_country_by_id(country_id: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        country_id, PlaceProperty.ID, engine, PlaceType.COUNTRY
    )


def get_province_by_id(province_id: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        province_id, PlaceProperty.ID, engine, PlaceType.PROVINCE
    )


def get_province_by_name(province: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        province, PlaceProperty.NAME, engine, PlaceType.PROVINCE
    )


def get_county_by_id(county_id: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(county_id, PlaceProperty.ID, engine, PlaceType.COUNTY)


def row_to_dict(
    rows: Iterable, table_or_cols: Union[str, Iterable[str]], engine: connection
) -> list[dict]:
    with engine.cursor() as cur:
        cur: cursor

        if type(table_or_cols) is str:
            cur.execute(
                (
                    "SELECT column_name "
                    'FROM information_schema."columns" '
                    "WHERE table_name=%s"
                    "ORDER BY ordinal_position"
                ),
                (table_or_cols,),
            )

            column_names = cur.fetchall()

            column_names = [column[0] for column in column_names]
        else:
            column_names = table_or_cols

        res: list[dict] = []

        for row in ensure_array(rows):
            mapped_row = {}
            for i, column_name in enumerate(column_names):
                mapped_row[column_name] = row[i]
            res.append(mapped_row)

        return res


def ensure_array(element) -> List:
    if not len(element):
        return []

    return element if isinstance(element[0], Iterable) else [element]


def create_country(country: dict, engine: connection) -> str:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            (
                "INSERT INTO countries "
                "VALUES ("
                "DEFAULT, "
                "%(name)s, "
                "%(alpha2)s, "
                "%(alpha3)s, "
                "ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326), "
                "NULL"
                ") "
                "RETURNING id"
            ),
            country,
        )

        result = cur.fetchone()

        engine.commit()

        return result[0]


def create_province(province: dict, engine: connection) -> str:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            (
                "INSERT INTO provinces VALUES ("
                "DEFAULT, "
                "%(name)s, "
                "ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326), "
                "NULL, "
                "%(code)s, "
                "%(country_id)s"
                ") RETURNING id"
            ),
            province,
        )

        result = cur.fetchone()

        engine.commit()

        return result[0]


def create_county(county: dict, engine: connection) -> str:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            (
                "INSERT INTO provinces VALUES ("
                "DEFAULT, "
                "%(name)s, "
                "ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326), "
                "NULL, "
                "%(code)s, "
                "%(province_id)s"
                ") RETURNING id"
            ),
            county,
        )

        result = cur.fetchone()

        engine.commit()

        return result[0]


def get_cases_by_country(
    country_id: int, engine: connection, case_type: CaseType = None
) -> List[Dict]:
    return get_cases_by_filters(engine, country_id=country_id, case_type=case_type)


def get_cases_by_province(
    province_id: int, engine: connection, case_type: CaseType = None
) -> List[Dict]:
    return get_cases_by_filters(engine, province_id=province_id, case_type=case_type)


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
    params = []
    constraints = []

    columns = ["amount"]
    select = sql.SQL("SELECT ")

    if len(aggregation):
        select += sql.SQL("sum(c.amount)")
        if Aggregations.DATE in aggregation:
            select += sql.SQL(", c.date")
            columns.append("date")
        if Aggregations.COUNTRY in aggregation:
            select += sql.SQL(", co.name as country")
            columns.append("country")
        if Aggregations.TYPE in aggregation:
            select += sql.SQL(", c.type")
            columns.append("type")
        if Aggregations.PROVINCE in aggregation:
            select += sql.SQL(", p.name as province, p.code as province_code")
    else:
        select += sql.SQL("c.amount, type, c.date, co.name")
        columns.append("type")
        columns.append("date")
        columns.append("country")

    from_ = sql.SQL("FROM cases c")

    query = sql.SQL("")

    query += sql.SQL("INNER JOIN countries co ON c.country_id = co.id ")

    if province_id:
        select += sql.SQL(",p.name as province, p.code as province_code")

    if province_id or Aggregations.PROVINCE in aggregation:
        query += sql.SQL("INNER JOIN provinces p ON c.province_id = p.id ")
        columns.append("province")
        columns.append("province_code")

    if country_id:
        constraints.append(sql.SQL("c.country_id=%s"))
        params.append(country_id)

    if province_id:
        constraints.append(sql.SQL("c.province_id=%s"))
        params.append(province_id)

    if date:
        constraints.append(sql.SQL("c.date=%s"))
        params.append(date)

    if date_lte:
        constraints.append(sql.SQL("c.date<=%s"))
        params.append(date_lte)

    if date_gte:
        constraints.append(sql.SQL("c.date>=%s"))
        params.append(date_gte)

    if case_type:
        constraints.append(sql.SQL("c.type=%s"))
        params.append(case_type.value)

    if len(constraints):
        query += sql.SQL(" WHERE ") + sql.SQL(" AND ").join(constraints)

    if len(aggregation):
        query += sql.SQL(" GROUP BY ")

        query += sql.SQL(", ").join(
            sql.SQL("{}").format(sql.Identifier(agg.value)) for agg in aggregation
        )

    if len(sort):
        query += sql.SQL(" ORDER BY")
        for field in sort:
            order = OrderBy.ASC

            if field.startswith("-"):
                order = OrderBy.DESC
                field = field[1:]

            query += sql.SQL(" {} " + f"{order.value}").format(sql.Identifier(field))

    if limit:
        query += sql.SQL(" LIMIT %s")
        params.append(limit)

    return {
        "select": select,
        "from": from_,
        "query": query,
        "params": tuple(params),
        "columns": tuple(columns),
    }


def get_cases_by_filters(
    engine: connection,
    country_id: int = None,
    province_id: int = None,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    aggregation: list[Aggregations] = [],
    limit: int = None,
    sort: list = [],
) -> List[Dict]:
    with engine.cursor() as cur:
        cur: cursor

        query = get_cases_by_filters_query(
            country_id,
            province_id,
            date,
            date_lte,
            date_gte,
            case_type,
            aggregation,
            limit,
            sort,
        )

        params = query.pop("params")
        columns = query.pop("columns")

        final_query = sql.SQL(" ").join([query[k] for k in query.keys()])
        cur.execute(final_query, params)

        return row_to_dict(cur.fetchall(), columns, engine)


def get_cum_cases_by_date(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
) -> List[Dict]:
    columns = ["type", "amount", "date", "country"]

    params = []

    inner_query = sql.SQL(
        (
            "SELECT c.type as type, sum(c.amount) as amount, "
            "c.date as date, co.name as country "
            "FROM cases c INNER JOIN countries co ON c.country_id = co.id "
        )
    )

    if date:
        inner_query += sql.SQL("WHERE date=%s")
        params.append(date)
    elif date_gte or date_lte:
        if date_gte:
            inner_query += sql.SQL("WHERE date>=%d")
            params.append(date_gte)

        if date_lte:
            if len(params):
                inner_query += sql.SQL("AND ")
            else:
                inner_query += sql.SQL("WHERE ")

            inner_query += sql.SQL("date<=%s")
            params.append(date_lte)

    if case_type:
        if len(params):
            inner_query += sql.SQL("AND ")
        else:
            inner_query += sql.SQL("WHERE ")

        inner_query += sql.SQL("type=%s")
        params.append(case_type.value)

    inner_query += sql.SQL(("GROUP BY c.date, c.type, co.name"))

    outter_query = (
        sql.SQL(
            (
                "SELECT "
                "type, "
                "sum(amount) OVER (PARTITION BY type, country ORDER BY date ASC), "
                "date, country FROM ( "
            )
        )
        + inner_query
        + sql.SQL((") as _ ORDER BY date ASC"))
    )

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(outter_query, tuple(params))

        return row_to_dict(cur.fetchall(), columns, engine)


def get_cum_cases_by_date_country(
    engine: connection,
    country_id: int,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
) -> List[Dict]:
    columns = ["type", "amount", "date", "province"]

    params: list[Any] = [country_id]

    inner_query = sql.SQL(
        (
            "SELECT c.type as type, sum(c.amount) as amount, "
            "c.date as date, p.name as province "
            "FROM cases c INNER JOIN provinces p ON c.province_id = p.id "
            "WHERE c.country_id=%s "
        )
    )

    if date:
        inner_query += sql.SQL("AND date=%s")
        params.append(date)
    elif date_gte or date_lte:
        if date_gte:
            inner_query += sql.SQL("AND date>=%d")
            params.append(date_gte)

        if date_lte:
            inner_query += sql.SQL("AND date<=%s")
            params.append(date_lte)

    if case_type:
        inner_query += sql.SQL("AND type=%s")
        params.append(case_type.value)

    inner_query += sql.SQL(("GROUP BY c.date, c.type, p.name"))

    outter_query = (
        sql.SQL(
            (
                "SELECT "
                "type, "
                "sum(amount) OVER (PARTITION BY type, province ORDER BY date ASC), "
                "date, province FROM ( "
            )
        )
        + inner_query
        + sql.SQL((") as _ ORDER BY date ASC"))
    )

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(outter_query, tuple(params))

        return row_to_dict(cur.fetchall(), columns, engine)


def get_cum_cases_by_country(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
) -> List[Dict]:
    columns = ["country", "amount", "date"]

    params = []

    inner_query = sql.SQL(
        (
            "SELECT co.name as country, sum(c.amount) as amount, c.date as date "
            "FROM cases c INNER JOIN countries co ON c.country_id = co.id "
        )
    )

    if date:
        inner_query += sql.SQL("WHERE date=%s")
        params.append(date)
    elif date_gte or date_lte:
        if date_gte:
            inner_query += sql.SQL("WHERE date>=%d")
            params.append(date_gte)

        if date_lte:
            if len(params):
                inner_query += sql.SQL("AND ")
            else:
                inner_query += sql.SQL("WHERE ")

            inner_query += sql.SQL("date<=%s")
            params.append(date_lte)

    if case_type:
        if len(params):
            inner_query += sql.SQL("AND ")
        else:
            inner_query += sql.SQL("WHERE ")

        inner_query += sql.SQL("type=%s")
        params.append(case_type.value)

    inner_query += sql.SQL(("GROUP BY c.date, co.name"))

    outter_query = (
        sql.SQL(
            (
                "SELECT "
                "country, "
                "sum(amount) OVER (PARTITION BY country ORDER BY date ASC), "
                "date FROM ( "
            )
        )
        + inner_query
        + sql.SQL((") as _ ORDER BY date ASC"))
    )

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(outter_query, tuple(params))

        return row_to_dict(cur.fetchall(), columns, engine)


def get_cum_cases_by_province(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    country_id: int = None,
) -> List[Dict]:
    columns = ["province", "amount", "date"]

    params: list[Any] = [country_id]

    inner_query = sql.SQL(
        (
            "SELECT p.name as province, sum(c.amount) as amount, c.date as date "
            "FROM cases c INNER JOIN provinces p ON c.province_id = p.id "
            "WHERE c.country_id=%s"
        )
    )

    if date:
        inner_query += sql.SQL("AND date=%s")
        params.append(date)
    elif date_gte or date_lte:
        if date_gte:
            inner_query += sql.SQL("AND date>=%d")
            params.append(date_gte)

        if date_lte:
            inner_query += sql.SQL("AND date<=%s")
            params.append(date_lte)

    if case_type:
        inner_query += sql.SQL("AND type=%s")
        params.append(case_type.value)

    inner_query += sql.SQL(("GROUP BY c.date, p.name"))

    outter_query = (
        sql.SQL(
            (
                "SELECT "
                "province, "
                "sum(amount) OVER (PARTITION BY province ORDER BY date ASC), "
                "date FROM ( "
            )
        )
        + inner_query
        + sql.SQL((") as _ ORDER BY date ASC"))
    )

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(outter_query, tuple(params))

        return row_to_dict(cur.fetchall(), columns, engine)


def create_case(
    case: dict,
    engine: connection,
    conflict_strategy: OnConflictStrategy = OnConflictStrategy.REPLACE,
) -> bool:
    with engine.cursor() as cur:
        cur: cursor

        query = (
            "INSERT INTO cases VALUES (DEFAULT, %(type)s, %(amount)s, %(date)s, %(country_id)s, "
            "%(province_id)s, %(county_id)s) "
            "ON CONFLICT ("
            "type, "
            "date, "
            "country_id, "
            "COALESCE(province_id, -1), COALESCE(county_id, -1)"
            ") DO UPDATE SET "
        )

        if conflict_strategy is OnConflictStrategy.ADD:
            query += "amount=cases.amount + %(amount)s"
        else:
            query += "amount=%(amount)s"

        cur.execute(query, case)

        engine.commit()

        return True


def get_all_countries(
    engine: connection, name: str = None, near: list[float] = []
) -> list[dict]:
    with engine.cursor() as cur:
        cur: cursor

        params = []

        query = sql.SQL("SELECT * FROM countries")

        if name:
            query += sql.SQL(" WHERE name=%s")
            params.append(name)

        if len(near):
            query += sql.SQL(
                " ORDER BY location <-> ST_SetSRID(ST_MakePoint(%s,%s), 4326)"
            )
            params.append(near[1])
            params.append(near[0])

        cur.execute(query, params)

        return row_to_dict(cur.fetchall(), "countries", engine)


def get_all_provinces(engine: connection) -> list[dict]:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL(
                (
                    "SELECT p.name as province, "
                    "p.id as province_id, "
                    "p.code as province_code, "
                    "c.name as country, "
                    "c.id as country_id "
                    "FROM provinces p INNER JOIN countries c ON p.country_id = c.id"
                )
            )
        )

        return row_to_dict(
            cur.fetchall(),
            ["province", "province_id", "province_code", "country", "country_id"],
            engine,
        )


def get_provinces_by_country(engine: connection, country_id: int) -> list[dict]:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL(
                (
                    "SELECT p.name as province, "
                    "p.id as province_id, "
                    "p.code as province_code, "
                    "c.name as country, "
                    "c.id as country_id "
                    "FROM provinces p INNER JOIN countries c ON p.country_id = c.id "
                    "WHERE p.country_id=%s"
                )
            ),
            (country_id,),
        )

        return row_to_dict(
            cur.fetchall(),
            ["province", "province_id", "province_code", "country", "country_id"],
            engine,
        )


def insert_api_key(engine: connection, hashed_key: str) -> bool:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL("INSERT INTO api_keys VALUES (DEFAULT, %s)"),
            (hashed_key,),
        )

        engine.commit()

        return True


def check_api_key(engine: connection, hashed_key: str) -> bool:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL("SELECT COUNT(*) FROM api_keys WHERE api_key=%s"),
            (hashed_key,),
        )

        res = int(cur.fetchone()[0])

        return res > 0
