FROM python:3.10-slim

RUN mkdir /app
RUN mkdir /app/src
COPY . /app

WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

