from datetime import datetime
from typing import List

import altair as alt
import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from ..charts import bar_rank, evolution_by_type, map_cases_contribution
from ..data import (
    get_abs_cases,
    get_all_countries,
    get_global_cases_by_type,
    get_global_cases_normalized,
    get_global_cumm_cases_by_country,
    get_global_cumm_cases_by_date,
    get_max_date_data,
    get_min_date_data,
)
from ..utils import Page


class GeneralData(Page):
    @st.cache
    def get_topo(self, url: str) -> alt.UrlData:
        return alt.topo_feature(url, "countries")

    def write(self):
        st.title("General Data")

        cols: List[DeltaGenerator] = st.columns(3)

        cases_data = get_global_cases_by_type()

        cols[0].header("Global confirmed cases")
        cols[0].subheader(
            f"{(cases_data[cases_data['type'] == 'confirmed']['amount']).iloc[0]:,}"
        )
        cols[0].text("")

        cols[1].header("Global death cases")
        cols[1].subheader(
            f"{(cases_data[cases_data['type'] == 'dead']['amount']).iloc[0]:,}"
        )
        cols[1].text("")

        cols[2].header("Global recovered cases")
        cols[2].subheader(
            f"{(cases_data[cases_data['type'] == 'recovered']['amount']).iloc[0]:,}"
        )

        cols: List[DeltaGenerator] = st.columns((1, 1, 3))

        min_date = get_min_date_data()
        max_date = get_max_date_data()

        dates: List[datetime] = cols[0].date_input(  # type: ignore
            "Date range",
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date],
        )

        if len(dates) < 2:
            st.stop()

        chart_type = cols[1].selectbox("Chart type", ["Cummulative", "Absolute"], 0)

        all_countries = pd.DataFrame.from_records(get_all_countries())

        countries = cols[2].multiselect(
            "Countries", all_countries["name"].unique().tolist()
        )

        countries_alpha = all_countries[all_countries["name"].isin(countries)][
            "alpha2"
        ].values

        if chart_type == "Cummulative":
            global_cases = get_global_cumm_cases_by_date(
                dates[0], dates[1], countries_alpha
            )
        else:
            global_cases = get_abs_cases(
                dates[0], dates[1], None, countries_alpha, None
            )

        st.header("Global cases evolution")

        st.altair_chart(evolution_by_type(global_cases), True)

        st.header("Global cases by country")

        cols: List[DeltaGenerator] = st.columns(2)

        rank_num = int(
            cols[0].number_input(
                "Top N countries",
                0,
                len(countries) or len(all_countries),
                len(countries) or min(len(all_countries), 30),
            )
            or len(countries)
            or len(all_countries)
        )

        case_type_rank = cols[1].selectbox(
            "Case type", ["confirmed", "recovered", "dead"], 0, key="case_type_rank"
        )

        case_type_rank_country = get_global_cumm_cases_by_country(
            dates[0], dates[1], countries_alpha, case_type_rank, rank_num
        )

        st.altair_chart(bar_rank(case_type_rank_country, "country"), True)

        url = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

        # Source of land data
        source = self.get_topo(url)

        case_type = st.selectbox(
            "Case type", ["confirmed", "recovered", "dead"], 0, key="case_type_map"
        )

        st.header(f"Countries contribution rate to {case_type} cases")

        global_cases = get_global_cases_normalized(dates[0], dates[1], case_type)

        st.altair_chart(
            map_cases_contribution(
                source,
                global_cases,
                [
                    alt.Tooltip("properties.name:N", title="Country"),
                    alt.Tooltip("amount:Q", title="Amount rate", format=".3%"),
                ],
                "properties.name",
                "country",
            ),
            True,
        )
