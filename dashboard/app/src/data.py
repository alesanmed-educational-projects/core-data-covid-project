from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
import streamlit as st

from .config import Config
from .types import CaseType, DataReturnType


def get_global_confirmed_by_date(
    date_from: datetime,
    date_to: datetime,
    return_type: DataReturnType = DataReturnType.DATAFRAME,
):
    days_difference = (date_to - date_from).days

    random_samples = np.random.randint(0, 10000, (days_difference, len(CaseType)))

    data = []

    for i in range(days_difference):
        date = date_from + timedelta(days=i)
        for idx, case_type in enumerate(CaseType):
            case = {
                "date": date,
                "cases": random_samples[i, idx],
                "type": case_type.value,
            }

            data.append(case)

    if return_type is DataReturnType.DATAFRAME:
        data = pd.DataFrame.from_records(data)

    return data


def get_cases_url(date_gte: datetime, date_lte: datetime) -> str:
    URL = Config().BACK_URL

    full_url = f"{URL}/cases?date[gte]={date_gte.strftime('%d-%m-%Y')}&date[lte]={date_lte.strftime('%d-%m-%Y')}"

    return full_url


def get_abs_cases_url(date_gte: datetime, date_lte: datetime) -> str:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases"
        f"?date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        "&agg=country"
        "&agg=date"
        "&agg=type"
    )

    return full_url


def get_global_cases_normalized(
    date_gte: datetime, date_lte: datetime, case_type: str = None
) -> str:
    URL = Config.BACK_URL

    full_url = (
        f"{URL}/cases"
        f"?date[gte]={date_gte}"
        f"&date[lte]={date_lte}"
        "&agg=country"
        "&agg=type"
        "&normalize=1"
    )

    if case_type:
        full_url = f"{full_url}&type={case_type}"

    return full_url


def get_country_cases_normalized(
    date_gte: datetime, date_lte: datetime, country: str, case_type: str = None
) -> str:
    URL = Config.BACK_URL

    country_info = requests.get(f"{URL}/countries?name={country}")

    country_info = country_info.json()[0]

    full_url = (
        f"{URL}/cases"
        f"?date[gte]={date_gte}"
        f"&date[lte]={date_lte}"
        "&agg=province"
        "&agg=type"
        "&normalize=1"
        f"&country={country_info['alpha2']}"
    )

    if case_type:
        full_url = f"{full_url}&type={case_type}"

    return full_url


@st.cache
def _get_max_min_date_data(max: bool) -> datetime:
    if max:
        sort = "-date"
    else:
        sort = "date"

    URL = Config().BACK_URL
    full_url = f"{URL}/cases?sort={sort}&limit=1"

    response = requests.get(full_url)

    case = response.json()[0]

    return datetime.strptime(case["date"], "%Y-%m-%d")


def get_min_date_data() -> datetime:
    return _get_max_min_date_data(False)


def get_max_date_data() -> datetime:
    return _get_max_min_date_data(True)


def get_global_cumm_cases_by_date_url(date_gte: datetime, date_lte: datetime) -> str:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases?resultType=cummulativeDate"
        f"&date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
    )

    return full_url


def get_global_cumm_cases_by_country_url(date_gte: datetime, date_lte: datetime) -> str:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases?resultType=cummulativeCountry"
        f"&date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
    )

    return full_url


@st.cache
def get_all_countries() -> list[str]:
    URL = Config().BACK_URL

    full_url = f"{URL}/countries"

    return [c["name"] for c in requests.get(full_url).json()]


@st.cache
def get_countries_with_province() -> list[str]:
    URL = Config().BACK_URL

    full_url = f"{URL}/provinces"

    response = requests.get(full_url)

    df = pd.DataFrame.from_records(response.json())

    return list(df["country"].unique())
