from typing import List

import altair as alt
import pandas as pd
import streamlit as st
from altair import datum
from streamlit.delta_generator import DeltaGenerator

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

        cols: List[DeltaGenerator] = st.beta_columns(3)

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

        cols: List[DeltaGenerator] = st.beta_columns((1, 1, 3))

        min_date = get_min_date_data()
        max_date = get_max_date_data()

        dates = cols[0].date_input(
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

        selection = alt.selection_multi(fields=["type"], bind="legend")

        base_chart: alt.Chart = alt.Chart(global_cases).mark_line(point=False)

        chart = (
            base_chart.transform_aggregate(
                total_amount="sum(amount)", groupby=["date", "type"]
            )
            .encode(
                x="yearmonthdate(date):T",
                y="total_amount:Q",
                tooltip=["date:T", "total_amount:Q"],
                color=alt.Color(
                    "type:N",
                    scale=alt.Scale(
                        domain=["confirmed", "dead", "recovered"],
                        range=["orange", "red", "green"],
                    ),
                ),
            )
            .transform_filter(selection)
            .add_selection(selection)
            .properties(height=500)
        )

        st.altair_chart(chart, True)

        global_positives_country = get_global_cumm_cases_by_country(
            dates[0], dates[1], countries_alpha
        )

        base_chart: alt.Chart = alt.Chart(global_positives_country)

        st.header("Global cases by country")

        rank_num = (
            st.number_input(
                "Top N countries",
                0,
                len(countries) or len(all_countries),
                len(countries) or 30,
            )
            or len(countries)
            or len(all_countries)
        )

        chart = (
            base_chart.transform_aggregate(
                sum_amount="sum(amount)", groupby=["country"]
            )
            .transform_window(
                rank="rank(sum_amount)",
                sort=[alt.SortField("sum_amount", order="descending")],
            )
            .transform_filter(datum.rank < rank_num + 1)
            .mark_bar()
            .encode(
                x="sum_amount:Q",
                y=alt.Y("country:N", sort="-x"),
                tooltip=["sum_amount:Q"],
                color="country:N",
            )
            .properties(height=900)
        )

        st.altair_chart(chart, True)

        url = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

        # Source of land data
        source = self.get_topo(url)

        case_type = st.selectbox("Case type", ["confirmed", "recovered", "dead"], 0)

        st.header(f"Countries contribution rate to {case_type} cases")

        global_cases = get_global_cases_normalized(dates[0], dates[1], case_type)

        # Layering and configuring the components
        chart = (
            alt.Chart(source)
            .mark_geoshape()
            .encode(
                color="amount:Q",
                tooltip=[
                    alt.Tooltip("properties.name:N", title="Country"),
                    alt.Tooltip("amount:Q", title="Amount rate", format=".3%"),
                ],
            )
            .transform_lookup(
                lookup="properties.name",
                from_=alt.LookupData(
                    global_cases,
                    "country",
                    ["amount"],
                ),
            )
            .properties(height=600)
        )

        st.altair_chart(chart, True)
