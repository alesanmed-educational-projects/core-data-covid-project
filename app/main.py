from src.pages import PAGES


def main():
    Page = PAGES["GeneralData"]

    Page().write()


if __name__ == "__main__":
    main()
