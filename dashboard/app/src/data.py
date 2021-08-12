from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from .config import Config


def get_global_cases_by_type() -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = f"{URL}/cases?agg=type"

    response = requests.get(full_url)

    data = pd.DataFrame.from_records(response.json())

    return data


def get_cases_url(date_gte: datetime, date_lte: datetime) -> str:
    URL = Config().BACK_URL

    full_url = f"{URL}/cases?date[gte]={date_gte.strftime('%d-%m-%Y')}&date[lte]={date_lte.strftime('%d-%m-%Y')}"

    return full_url


def get_abs_cases_url(
    date_gte: datetime,
    date_lte: datetime,
    agg_place: str = "country",
    country_code: str = None,
) -> str:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases"
        f"?date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        f"&agg={agg_place}"
        "&agg=date"
        "&agg=type"
    )

    if agg_place == "province":
        full_url = f"{full_url}&agg=province_code"

    if country_code:
        full_url = f"{full_url}&country={country_code}"

    return full_url


def get_global_cases_normalized(
    date_gte: datetime, date_lte: datetime, case_type: str = None
) -> str:
    URL = Config().BACK_URL

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


def get_country(country_name: str) -> dict:
    URL = Config().BACK_URL
    country_info = requests.get(f"{URL}/countries?name={country_name}")

    country_info = country_info.json()

    return country_info


def get_country_cases_normalized(
    date_gte: datetime, date_lte: datetime, country: str, case_type: str = None
) -> str:
    URL = Config().BACK_URL

    country_info = get_country(country)[0]

    full_url = (
        f"{URL}/cases"
        f"?date[gte]={date_gte}"
        f"&date[lte]={date_lte}"
        "&agg=province"
        "&agg=type"
        "&agg=province_code"
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


def get_closest_country(lat, long) -> dict:
    URL = Config().BACK_URL

    full_url = f"{URL}/countries?near={lat},{long}"

    country_res = requests.get(full_url)

    return country_res.json()[0]


def get_country_cumm_cases_by_date_url(
    date_gte: datetime, date_lte: datetime, country_code: str
) -> str:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases?resultType=cummulativeDateCountry"
        f"&date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        f"&country={country_code}"
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


def get_global_cumm_cases_by_province_url(
    date_gte: datetime, date_lte: datetime, country: str
) -> str:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases?resultType=cummulativeProvince"
        f"&date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        f"&country={country}"
    )

    return full_url


@st.cache
def get_all_countries() -> list[str]:
    URL = Config().BACK_URL

    full_url = f"{URL}/countries"

    return [c["name"] for c in requests.get(full_url).json()]


@st.cache
def get_all_provinces(country: str) -> list[str]:
    URL = Config().BACK_URL

    country_info = get_country(country)[0]

    full_url = f"{URL}/countries/{country_info['id']}/provinces"

    return [p["province"] for p in requests.get(full_url).json()]


@st.cache
def get_countries_with_province() -> list[str]:
    URL = Config().BACK_URL

    full_url = f"{URL}/provinces"

    response = requests.get(full_url)

    df = pd.DataFrame.from_records(response.json())

    return list(df["country"].unique())


def send_pdf_to_email(file: bytes, email: str) -> bool:
    URL = Config().BACK_URL

    full_url = f"{URL}/email"

    files = {"file": ("country_data.pdf", file, "application/json")}
    values = {"recipient": email}

    response = requests.post(full_url, files=files, data=values)

    return response.status_code < 400


def check_auth(key: str) -> bool:
    URL = Config().BACK_URL

    full_url = f"{URL}/auth"

    response = requests.post(full_url, headers={"Authorization": f"Bearer {key}"})

    return response.status_code < 400


def create_country(
    name: str, alpha2: str, alpha3: str, lat: float, lng: float, api_key
) -> bool:
    URL = Config().BACK_URL

    full_url = f"{URL}/countries"

    country_data = {
        "name": name,
        "alpha2": alpha2,
        "alpha3": alpha3,
        "lat": lat,
        "lng": lng,
    }

    response = requests.post(
        full_url,
        json=country_data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
    )

    return response.status_code < 400
