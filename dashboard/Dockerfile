FROM python:3.9.6-slim-buster

WORKDIR /covid-dashboard

ADD requirements.txt /covid-dashboard

RUN pip install -r requirements.txt

ADD . /covid-dashboard

EXPOSE $FRONT_PORT

CMD streamlit run --server.enableCORS false --server.enableXsrfProtection false --browser.serverAddress $SERVER_ADDRESS --browser.serverPort 443 --server.port $FRONT_PORT --server.address 0.0.0.0 --server.headless true app/main.py
