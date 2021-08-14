FROM python:3.9.6-slim-buster

WORKDIR /covid-dashboard

ADD requirements.txt /covid-dashboard

RUN pip install -r requirements.txt

ADD . /covid-dashboard

EXPOSE $FRONT_PORT

CMD streamlit run app/main.py
