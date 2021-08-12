from datetime import date, datetime
from decimal import Decimal
from typing import Dict

import pandas as pd
from werkzeug.datastructures import MultiDict


def parse_request_args(args: MultiDict[str, str]) -> Dict:
    res = {}

    for k in args.keys():
        if k.endswith("[lte]"):
            key = k.replace("[lte]", "")
            subkey = "lte"
        elif k.endswith("[gte]"):
            key = k.replace("[gte]", "")
            subkey = "gte"
        else:
            key = k
            subkey = None

        if key not in res:
            res[key] = {}

        if subkey:
            res[key][subkey] = args[k]
        else:
            res[key] = args[k]

    return res


def serialize_json(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return int(obj)

    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def normalize_json_col(json: list[dict], col: str) -> list[dict]:
    df = pd.DataFrame.from_records(json)

    df[col] = (df[col] / df[col].sum()).astype(float)

    return df.to_dict("records")
