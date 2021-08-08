from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from .types import CaseType, DataReturnType


def get_global_positives_by_date(
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
