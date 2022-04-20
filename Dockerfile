FROM python:3.10-slim

RUN apt-get update
RUN apt-get -y install curl
RUN apt-get -y install jq

RUN mkdir /app
COPY . /app
WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry==1.1.13
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
ENTRYPOINT [ "sh", "scripts/run_cloud.sh" ]
