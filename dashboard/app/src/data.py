from datetime import datetime
from typing import Iterable, List, Optional

import pandas as pd
import requests
import streamlit as st
from pandas._typing import ArrayLike

from .config import Config

HOUR = 3600


@st.cache(suppress_st_warning=True, ttl=(12 * HOUR))
def get_global_cases_by_type() -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = f"{URL}/cases?agg=type"

    response = requests.get(full_url)

    data = pd.DataFrame.from_records(response.json())

    return data


@st.cache(show_spinner=False)
def get_cases(date_gte: datetime, date_lte: datetime) -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = f"{URL}/cases?date[gte]={date_gte.strftime('%d-%m-%Y')}&date[lte]={date_lte.strftime('%d-%m-%Y')}"

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
def get_abs_cases(
    date_gte: datetime,
    date_lte: datetime,
    agg_place: Optional[str],
    countries: Iterable[str] = None,
    provinces: Iterable[str] = None,
) -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases"
        f"?date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        "&agg=date"
        "&agg=type"
    )

    if agg_place:
        if agg_place == "province":
            full_url = f"{full_url}&agg=province_code"
        elif agg_place == "country":
            full_url = f"{full_url}&agg=country"

    if countries is not None:
        full_url = f"{full_url}" + f"&country={'&country='.join(countries)}"

    if provinces is not None:
        full_url = f"{full_url}" + f"&province={'&province='.join(provinces)}"

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
def get_global_cases_normalized(
    date_gte: datetime, date_lte: datetime, case_type: str = None
) -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases"
        f"?date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        "&agg=country"
        "&agg=type"
        "&normalize=1"
    )

    if case_type:
        full_url = f"{full_url}&type={case_type}"

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
def get_country(country_name: str) -> dict:
    URL = Config().BACK_URL
    country_info = requests.get(f"{URL}/countries?name={country_name}")

    country_info = country_info.json()

    return country_info


@st.cache(show_spinner=False)
def get_country_cases_normalized(
    date_gte: datetime, date_lte: datetime, country: str, case_type: str = None
) -> pd.DataFrame:
    URL = Config().BACK_URL

    country_info = get_country(country)[0]

    full_url = (
        f"{URL}/cases"
        f"?date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        "&agg=province"
        "&agg=type"
        "&agg=province_code"
        "&normalize=1"
        f"&country={country_info['alpha2']}"
    )

    if case_type:
        full_url = f"{full_url}&type={case_type}"

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
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


@st.cache(show_spinner=False)
def get_min_date_data() -> datetime:
    return _get_max_min_date_data(False)


@st.cache(show_spinner=False)
def get_max_date_data() -> datetime:
    return _get_max_min_date_data(True)


@st.cache(show_spinner=False)
def get_global_cumm_cases_by_date(
    date_gte: datetime, date_lte: datetime, countries: Iterable[str] = []
) -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases?resultType=cummulativeDate"
        f"&date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        f"&country={'&country='.join(countries)}"
    )

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
def get_closest_country(lat, long) -> dict:
    URL = Config().BACK_URL

    full_url = f"{URL}/countries?near={lat},{long}"

    country_res = requests.get(full_url)

    return country_res.json()[0]


@st.cache(show_spinner=False)
def get_country_cumm_cases_by_date(
    date_gte: datetime,
    date_lte: datetime,
    country_code: str,
    provinces: Iterable[str] = [],
) -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases?resultType=cummulativeDateCountry"
        f"&date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        f"&country={country_code}"
        f"&province={'&province='.join(provinces)}"
    )

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
def get_global_cumm_cases_by_country(
    date_gte: datetime,
    date_lte: datetime,
    countries: ArrayLike,
    case_type: str,
    limit: int,
) -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases?resultType=cummulativeCountry"
        f"&date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        f"&country={'&country='.join(countries)}"
        f"&type={case_type}"
        f"&limit={limit}"
    )

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
def get_global_cumm_cases_by_province(
    date_gte: datetime,
    date_lte: datetime,
    country: str,
    provinces: List[str],
    case_type: str,
) -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = (
        f"{URL}/cases?resultType=cummulativeProvince"
        f"&date[gte]={date_gte.strftime('%d-%m-%Y')}"
        f"&date[lte]={date_lte.strftime('%d-%m-%Y')}"
        f"&country={country}"
        f"&province={'&province='.join(provinces)}"
        f"&type={case_type}"
    )

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
def get_all_countries() -> pd.DataFrame:
    URL = Config().BACK_URL

    full_url = f"{URL}/countries"

    data = pd.DataFrame.from_records(requests.get(full_url).json())

    return data


@st.cache(show_spinner=False)
def get_all_provinces(country: str) -> list[str]:
    URL = Config().BACK_URL

    country_info = get_country(country)[0]

    full_url = f"{URL}/countries/{country_info['id']}/provinces"

    return [p["province"] for p in requests.get(full_url).json()]


@st.cache(show_spinner=False)
def get_countries_with_province() -> list[str]:
    URL = Config().BACK_URL

    full_url = f"{URL}/provinces"

    response = requests.get(full_url)

    df = pd.DataFrame.from_records(response.json())

    return list(df["country"].unique())


@st.cache(show_spinner=False)
def send_pdf_to_email(file: bytes, email: str) -> bool:
    URL = Config().BACK_URL

    full_url = f"{URL}/email"

    files = {"file": ("country_data.pdf", file, "application/json")}
    values = {"recipient": email}

    response = requests.post(full_url, files=files, data=values)

    return response.status_code < 400


@st.cache(show_spinner=False)
def check_auth(key: str) -> bool:
    URL = Config().BACK_URL

    full_url = f"{URL}/auth"

    response = requests.post(full_url, headers={"Authorization": f"Bearer {key}"})

    return response.status_code < 400


@st.cache(show_spinner=False)
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
