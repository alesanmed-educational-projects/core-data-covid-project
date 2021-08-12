import locale

import streamlit as st
from src.pages import PAGES


def main():
    st.set_page_config(layout="wide")

    page = st.sidebar.radio("Go to", list(PAGES.keys()))

    Page = PAGES[page]

    Page().write()


if __name__ == "__main__":
    main()
