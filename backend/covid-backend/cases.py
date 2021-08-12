import json
from datetime import datetime
from http import HTTPStatus
from typing import Optional

from covid_data.db.queries import (get_cases_by_filters, get_country_by_alpha2,
                                   get_country_by_alpha3,
                                   get_cum_cases_by_country,
                                   get_cum_cases_by_date,
                                   get_cum_cases_by_date_country,
                                   get_cum_cases_by_province,
                                   get_province_by_name)
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

    case_type: Optional[str] = args.get("type", None)

    if case_type is not None and case_type.lower() not in {
        t.value for t in CaseType.__members__.values()
    }:
        raise exceptions.BadRequest(f"Case type {case_type} not valid")

    case_type_fix = None
    if case_type:
        case_type_fix = CaseType(case_type)

    agg: list[str] = args["agg"]
    agg_fix: list[Aggregations] = []

    if len(agg):
        for agg_val in agg:
            if agg_val.lower() not in {
                t.value for t in Aggregations.__members__.values()
            }:
                raise exceptions.BadRequest(f"Aggregation {agg} not valid")
            else:
                agg_fix.append(Aggregations(agg_val))

    result_type: Optional[str] = args.get("resultType", None)

    if result_type is not None and result_type not in {
        t.value for t in ResultType.__members__.values()
    }:
        raise exceptions.BadRequest(f"Result type {result_type} not valid")

    result_type_fix = None
    if result_type:
        result_type_fix = ResultType(result_type)

    country = args.get("country", None)

    if country is not None and 1 >= len(country) > 3:
        raise exceptions.BadRequest(
            f"Country {country} is not an Alpha2 or Alpha3 code"
        )

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
        if hasattr(date_dict, "lte"):
            try:
                date_lte = datetime.strptime(date_dict["lte"], "%d-%m-%Y")
            except exceptions.BadRequest:
                raise exceptions.BadRequest(
                    f"Date {date_dict['lte']} is not in DD/MM/YYYY format"
                )

        if hasattr(date_dict, "gte"):
            try:
                date_gte = datetime.strptime(date_dict["gte"], "%d-%m-%Y")
            except exceptions.BadRequest:
                raise exceptions.BadRequest(
                    f"Date {date_dict['gte']} is not in DD/MM/YYYY format"
                )

    country_id = None
    if country:
        if len(country) == 3:
            country = get_country_by_alpha3(country, db)
        else:
            country = get_country_by_alpha2(country, db)

        if not country:
            return []

        country_id = country["id"]

    province_id = None
    if province:
        province = get_province_by_name(province, db)

        if not province:
            return []

        province_id = province["id"]

    limit = args.get("limit", None)

    if limit:
        try:
            limit = int(limit)
            if limit < 0:
                raise exceptions.BadRequest()
        except exceptions.BadRequest:
            raise exceptions.BadRequest(f"Invalid limit value {limit}")

    if result_type_fix and result_type_fix is ResultType.CUMMULATIVE_DATE:
        cases = get_cum_cases_by_date(db, date, date_lte, date_gte, case_type_fix)
    elif result_type_fix is ResultType.CUMMULATIVE_DATE_COUNTRY:
        if not country_id:
            raise exceptions.BadRequest(
                "A country is required when requesting this type of result"
            )
        cases = get_cum_cases_by_date_country(
            db, country_id, date, date_lte, date_gte, case_type_fix
        )
    elif result_type_fix is ResultType.CUMMULATIVE_PROVINCE:
        if not country_id:
            raise exceptions.BadRequest(
                "A country is required when requesting this type of result"
            )
        cases = get_cum_cases_by_province(
            db, date, date_lte, date_gte, case_type_fix, country_id
        )
    elif result_type_fix:
        cases = get_cum_cases_by_country(db, date, date_lte, date_gte, case_type_fix)
    else:
        cases = get_cases_by_filters(
            db,
            country_id,
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
