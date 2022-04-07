FROM python:3.10-slim

RUN mkdir /src 
COPY /src /src

COPY pyproject.toml /app 
WORKDIR /src

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

