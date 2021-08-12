from typing import Dict, Type

from src.utils import Page

from .amend_data import AmendData
from .country_data import CountryData
from .general_data import GeneralData

PAGES: Dict[str, Type[Page]] = {
    "GeneralData": GeneralData,
    "CountryData": CountryData,
    "ManageData": AmendData,
}

__all__ = ["PAGES"]
