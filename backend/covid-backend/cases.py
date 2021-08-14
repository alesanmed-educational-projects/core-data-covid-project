import json
from datetime import datetime
from http import HTTPStatus
from typing import Optional

from covid_data.db.queries import (
    get_cases_by_filters,
    get_countries_id_by_alpha2,
    get_cum_cases_by_country,
    get_cum_cases_by_date,
    get_cum_cases_by_date_country,
    get_cum_cases_by_province,
    get_province_by_name,
)
from covid_data.types import Aggregations, CaseType
from flask import Blueprint, request
from flask.wrappers import Response
from werkzeug import exceptions

from .db import get_db
from .types import ResultType
from .utils import normalize_json_col, parse_request_args, serialize_json

bp = Blueprint("cases", __name__, url_prefix="/cases")


@bp.route("", methods=["GET"])
def get_cases():
    db = get_db()

    args = parse_request_args(request.args)
    args["sort"] = request.args.getlist("sort") or []
    args["agg"] = request.args.getlist("agg") or []
    args["countries"] = list(filter(len, (request.args.getlist("country") or [])))

    case_type: Optional[str]

    if (case_type := args.get("type", None)) and case_type.lower() not in {
        t.value for t in CaseType.__members__.values()
    }:
        raise exceptions.BadRequest(f"Case type {case_type} not valid")

    case_type_fix = CaseType(case_type) if case_type else None

    agg: list[str]
    agg_fix: list[Aggregations] = []

    if len(agg := args["agg"]):
        for agg_val in agg:
            if agg_val.lower() not in {
                t.value for t in Aggregations.__members__.values()
            }:
                raise exceptions.BadRequest(f"Aggregation {agg} not valid")
            else:
                agg_fix.append(Aggregations(agg_val))

    result_type: Optional[str]

    if (result_type := args.get("resultType", None)) and result_type not in {
        t.value for t in ResultType.__members__.values()
    }:
        raise exceptions.BadRequest(f"Result type {result_type} not valid")

    result_type_fix = ResultType(result_type) if result_type else None

    countries: list[str]
    if countries := args.get("countries", []):
        for country in countries:
            if len(country) != 2:
                raise exceptions.BadRequest(f"Country {country} is not an Alpha2 code")

    province = args.get("province", None)

    date = None
    date_lte = None
    date_gte = None

    if type(args.get("date", None)) is str:
        try:
            date = datetime.strptime(args.get("date", ""), "%d-%m-%Y")
        except exceptions.BadRequest:
            raise exceptions.BadRequest(
                f"Date {args.get('date', '')} is not in DD/MM/YYYY format"
            )
    elif type(args.get("date", None)) is dict:
        date_dict = args["date"]
        if "lte" in date_dict:
            try:
                date_lte = datetime.strptime(date_dict["lte"], "%d-%m-%Y")
            except exceptions.BadRequest:
                raise exceptions.BadRequest(
                    f"Date {date_dict['lte']} is not in DD/MM/YYYY format"
                )

        if "gte" in date_dict:
            try:
                date_gte = datetime.strptime(date_dict["gte"], "%d-%m-%Y")
            except exceptions.BadRequest:
                raise exceptions.BadRequest(
                    f"Date {date_dict['gte']} is not in DD/MM/YYYY format"
                )

    countries_id = get_countries_id_by_alpha2(countries, db) if len(countries) else []

    province_id = None
    if province:
        province = get_province_by_name(province, db)

        if not province:
            return []

        province_id = province["id"]

    if limit := args.get("limit", None):
        try:
            limit = int(limit)
            if limit < 0:
                raise exceptions.BadRequest()
        except exceptions.BadRequest:
            raise exceptions.BadRequest(f"Invalid limit value {limit}")

    if result_type_fix and result_type_fix is ResultType.CUMMULATIVE_DATE:
        cases = get_cum_cases_by_date(
            db, date, date_lte, date_gte, case_type_fix, countries_id
        )
    elif result_type_fix is ResultType.CUMMULATIVE_DATE_COUNTRY:
        if not len(countries_id):
            raise exceptions.BadRequest(
                "A country is required when requesting this type of result"
            )
        cases = get_cum_cases_by_date_country(
            db, countries_id[0], date, date_lte, date_gte, case_type_fix
        )
    elif result_type_fix is ResultType.CUMMULATIVE_PROVINCE:
        if not len(countries_id):
            raise exceptions.BadRequest(
                "A country is required when requesting this type of result"
            )
        cases = get_cum_cases_by_province(
            db, date, date_lte, date_gte, case_type_fix, countries_id[0]
        )
    elif result_type_fix:
        cases = get_cum_cases_by_country(
            db, date, date_lte, date_gte, case_type_fix, countries_id
        )
    else:
        cases = get_cases_by_filters(
            db,
            countries_id,
            province_id,
            date,
            date_lte,
            date_gte,
            case_type_fix,
            agg_fix,
            limit,
            args.get("sort", []),
        )

    if args.get("normalize", None):
        cases = normalize_json_col(cases, "amount")

    return Response(
        json.dumps(cases, default=serialize_json),
        HTTPStatus.OK,
        {"content-type": "application/json"},
    )
