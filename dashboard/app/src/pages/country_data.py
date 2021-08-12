import base64
from datetime import datetime
from typing import List

import altair as alt
import streamlit as st
from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from fpdf import FPDF
from streamlit.delta_generator import DeltaGenerator
from streamlit_bokeh_events import streamlit_bokeh_events

from ..data import (
    get_abs_cases_url,
    get_all_provinces,
    get_closest_country,
    get_countries_with_province,
    get_country,
    get_country_cases_normalized,
    get_country_cumm_cases_by_date_url,
    get_global_cumm_cases_by_province_url,
    get_max_date_data,
    get_min_date_data,
)
from ..utils import Page

TOPOJSON_MAP = {
    "Spain": {
        "url": (
            "https://raw.githubusercontent.com/"
            "alesanmed-educational-projects/"
            "core-data-covid-project/main/assets/"
            "topojson/spain-comunidad-with-canary-islands.json"
        ),
        "property": "ESP_adm1",
        "key": "properties.HASC_1",
    },
    "Canada": {
        "url": (
            "https://raw.githubusercontent.com/"
            "alesanmed-educational-projects/"
            "core-data-covid-project/main/assets/"
            "topojson/canadaprovtopo.json"
        ),
        "property": "canadaprov",
        "key": "id",
    },
}


class CountryData(Page):
    pdf: FPDF
    TITLE_FONT = ["Arial", "b", 16]
    SUBTITLE_FONT = ["Arial", "b", 14]
    BODY_FONT = ["Arial", "", 11]

    @st.cache
    def get_chart_from_url(self, url: str) -> alt.Chart:
        return alt.Chart(url)

    @st.cache
    def get_topo(self, url: str, property) -> alt.UrlData:
        return alt.topo_feature(url, property)

    def create_pdf(self):
        alt.renderers.enable("altair_saver", fmts=["png"])
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font(*self.TITLE_FONT)

        self.pdf = pdf

    def write(self):
        pdf_export = st.button("Export as PDF")

        title = "Country Data"

        st.title(title)

        if pdf_export:
            self.create_pdf()
            self.pdf.cell(0, 10, title, 0, 1, "C")

        cols: List[DeltaGenerator] = st.beta_columns((1, 3))

        min_date = get_min_date_data()
        max_date = get_max_date_data()

        date_title = "Date range"

        dates: list[datetime] = cols[0].date_input(
            date_title,
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date],
        )

        if pdf_export:
            self.pdf.set_font(*self.SUBTITLE_FONT)
            self.pdf.cell(0, 10, date_title, 0, 1)
            self.pdf.set_font(*self.BODY_FONT)
            self.pdf.cell(190 // 4, 10, dates[0].strftime("%d-%m-%Y"), 0, 0)
            self.pdf.cell(190 // 3, 10, dates[1].strftime("%d-%m-%Y"), 0, 1)

        available_countries = get_countries_with_province()

        selected_country = st.selectbox(
            "Country to view data for", ["-"] + available_countries
        )
        country_info = None

        st.write("Or...")

        loc_button = Button(label="Get Location")
        loc_button.js_on_event(  # type: ignore
            "button_click",
            CustomJS(
                code=(
                    "navigator.geolocation.getCurrentPosition("
                    "(loc) => {"
                    "document.dispatchEvent(new CustomEvent('GET_LOCATION', "
                    "{detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))"
                    "}"
                    ")"
                )
            ),
        )
        result = streamlit_bokeh_events(
            loc_button,
            events="GET_LOCATION",
            key="get_location",
            refresh_on_update=False,
            override_height=75,
            debounce_time=0,
        )

        if result:
            if "GET_LOCATION" in result:
                latlong = result.get("GET_LOCATION")

                country = get_closest_country(latlong["lat"], latlong["lon"])

                selected_country = country["name"]
                country_info = country

        if selected_country == "-":
            if pdf_export:
                st.warning("You have to select a country in order to export a PDF")

            st.stop()

        if not country_info:
            country_info = get_country(selected_country)[0]

        if pdf_export:
            self.pdf.set_font(*self.SUBTITLE_FONT)
            self.pdf.cell(0, 10, "Selected country", 0, 1)
            self.pdf.set_font(*self.BODY_FONT)
            self.pdf.cell(0, 10, country_info["name"], 0, 1)

        if selected_country in TOPOJSON_MAP:
            source = self.get_topo(
                TOPOJSON_MAP[selected_country]["url"],
                TOPOJSON_MAP[selected_country]["property"],
            )

            case_type = st.selectbox("Case type", ["confirmed", "recovered", "dead"], 0)

            contribution_title = f"States contribution rate to {case_type} cases"

            st.header(contribution_title)

            country_cases_url = get_country_cases_normalized(
                dates[0], dates[1], selected_country, case_type
            )

            # Layering and configuring the components
            chart: alt.Chart = (
                alt.Chart(source)
                .mark_geoshape()
                .encode(
                    color="amount:Q",
                    tooltip=[
                        alt.Tooltip("properties.NAME_1:N", title="State"),
                        alt.Tooltip("amount:Q", title="Amount rate", format=".2%"),
                    ],
                )
                .transform_lookup(
                    lookup=TOPOJSON_MAP[selected_country]["key"],
                    from_=alt.LookupData(
                        alt.UrlData(country_cases_url, alt.JsonDataFormat()),
                        "province_code",
                        ["amount"],
                    ),
                )
                .properties(height=600)
            )

            st.altair_chart(chart, True)

            if pdf_export:
                img_name = "./assets/provinces_contributions.png"
                # save(chart, img_name, method="selenium") Deactivated

                self.pdf.set_font(*self.SUBTITLE_FONT)
                self.pdf.cell(0, 10, contribution_title, 0, 1)
                self.pdf.set_font(*self.BODY_FONT)
                self.pdf.cell(0, 10, country_info["name"], 0, 1)
                self.pdf.image(img_name, w=180)

        cols: List[DeltaGenerator] = st.beta_columns((1, 3))

        chart_type_title = "Chart type"

        chart_type = cols[0].selectbox(chart_type_title, ["Cummulative", "Absolute"], 0)

        selected_provinces_title = "Provinces"

        all_provinces = get_all_provinces(selected_country)
        provinces = cols[1].multiselect(selected_provinces_title, all_provinces)

        if chart_type == "Cummulative":
            province_cases_url = get_country_cumm_cases_by_date_url(
                dates[0], dates[1], country_info["alpha2"]
            )
        else:
            province_cases_url = get_abs_cases_url(
                dates[0], dates[1], "province", country_info["alpha2"]
            )

        if pdf_export:
            self.pdf.set_font(*self.SUBTITLE_FONT)
            self.pdf.cell(0, 10, chart_type_title, 0, 1)
            self.pdf.set_font(*self.BODY_FONT)
            self.pdf.cell(0, 10, chart_type, 0, 1)
            self.pdf.set_font(*self.BODY_FONT)
            self.pdf.cell(0, 10, selected_provinces_title, 0, 1)
            for province in provinces if len(provinces) else all_provinces:
                self.pdf.cell(0, 10, f"\t- {province}", 0, 1)

        cols: List[DeltaGenerator] = st.beta_columns(2)

        country_header_title = f"{selected_country} cases evolution"
        province_header_title = "Global cases by province"

        cols[0].header(country_header_title)

        selection = alt.selection_multi(fields=["type"], bind="legend")

        base_chart: alt.Chart = self.get_chart_from_url(province_cases_url).mark_line(
            point=False
        )

        if len(provinces):
            base_chart = base_chart.transform_filter(
                alt.FieldOneOfPredicate("province", provinces)
            )

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

        cols[0].altair_chart(chart, True)

        if pdf_export:
            self.pdf.set_font(*self.SUBTITLE_FONT)
            self.pdf.cell(0, 20, country_header_title, 0, 1)
            self.pdf.image("./assets/country_evolution.png", w=180)

        province_positivies_url = get_global_cumm_cases_by_province_url(
            dates[0], dates[1], country_info["alpha2"]
        )

        base_chart = self.get_chart_from_url(province_positivies_url)

        if len(provinces):
            base_chart = base_chart.transform_filter(
                alt.FieldOneOfPredicate("province", provinces)
            )

        cols[1].header(province_header_title)

        chart = (
            base_chart.transform_aggregate(
                sum_amount="sum(amount)", groupby=["province"]
            )
            .mark_bar()
            .encode(
                x="sum_amount:Q",
                y=alt.Y("province:N", sort="-x"),
                tooltip=["sum_amount:Q"],
                color="province:N",
            )
            .properties(height=500)
        )

        cols[1].altair_chart(chart, True)

        if pdf_export:
            self.pdf.set_font(*self.SUBTITLE_FONT)
            self.pdf.cell(0, 20, province_header_title, 0, 1)
            self.pdf.image("./assets/cases_by_province.png", w=180)
            pdf_str = base64.b64encode(
                self.pdf.output(dest="S").encode("latin-1")
            ).decode()
            st.markdown(
                (
                    '<a download="country_data.pdf" '
                    f'href="data:application/pdf;base64,{pdf_str}">Download PDF</a>'
                ),
                unsafe_allow_html=True,
            )
