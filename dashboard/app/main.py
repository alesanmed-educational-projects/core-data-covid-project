from src.pages import PAGES


def main():
    Page = PAGES["CountryData"]

    Page().write()


if __name__ == "__main__":
    main()
