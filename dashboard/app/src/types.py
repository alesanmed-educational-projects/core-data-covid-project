from datetime import datetime
from enum import Enum, IntEnum
from typing import TypedDict


class CaseType(Enum):
    CONFIRMED = "confirmed"
    DEAD = "dead"
    RECOVERED = "recovered"


class Case(TypedDict):
    date: datetime
    cases: int
    type: CaseType


class DataReturnType(IntEnum):
    DATAFRAME = 1
    DICT = 2
