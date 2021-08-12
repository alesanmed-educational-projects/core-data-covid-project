from enum import Enum


class ResultType(Enum):
    CUMMULATIVE_DATE = "cummulativeDate"
    CUMMULATIVE_DATE_COUNTRY = "cummulativeDateCountry"
    CUMMULATIVE_COUNTRY = "cummulativeCountry"
    CUMMULATIVE_PROVINCE = "cummulativeProvince"
