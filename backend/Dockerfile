FROM python:3.9.6-slim-buster

RUN apt-get update
RUN apt-get install -y libpq-dev build-essential

RUN apt-get clean autoclean
RUN apt-get autoremove --yes
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/

WORKDIR /covid-back

ADD requirements.txt /covid-back

RUN pip install -r requirements.txt

ADD . /covid-back

EXPOSE $BACK_PORT

ENV FLASK_APP=covid-backend
ENV FLASK_ENV=production

CMD gunicorn --bind 0.0.0.0:$BACK_PORT --access-logfile - --log-level debug covid-backend.wsgi:app
