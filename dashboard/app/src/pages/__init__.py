from typing import Dict, Type

from src.utils import Page

from .general_data import GeneralData

PAGES: Dict[str, Type[Page]] = {"GeneralData": GeneralData}

__all__ = ["PAGES"]
