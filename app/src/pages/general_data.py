from datetime import datetime

import altair as alt
import streamlit as st
from pandas.core.frame import DataFrame

from ..data import get_global_positives_by_date
from ..utils import Page


class GeneralData(Page):
    def write(self):
        st.set_page_config(layout="wide")

        st.title("General Data")

        cols = st.beta_columns(3)

        cols[0].header("Global confirmed cases")
        cols[0].subheader(123456)

        cols[1].header("Global death cases")
        cols[1].subheader(123456)

        cols[2].header("Global recovered cases")
        cols[2].subheader(123456)

        global_positives = get_global_positives_by_date(
            datetime(2020, 1, 1), datetime.now()
        )

        st.header("Global cases evolution")
        if isinstance(global_positives, DataFrame):
            chart = (
                alt.Chart(global_positives)
                .mark_line(point=True)
                .encode(x="date", y="cases", tooltip=["date", "cases"], color="type")
            )
            st.altair_chart(chart, True)
