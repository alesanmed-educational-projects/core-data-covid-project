from typing import Dict, Type

from src.utils import Page

from .country_data import CountryData
from .general_data import GeneralData

PAGES: Dict[str, Type[Page]] = {"GeneralData": GeneralData, "CountryData": CountryData}

__all__ = ["PAGES"]
