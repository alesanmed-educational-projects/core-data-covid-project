FROM python:3.9.6-slim-buster

WORKDIR /covid-dashboard

ADD requirements.txt /covid-dashboard

RUN pip install -r requirements.txt

ADD . /covid-dashboard

EXPOSE $PORT

CMD streamlit run --server.enableXsrfProtection false --server.enableCORS false --server.port $PORT --server.headless true app/main.py
