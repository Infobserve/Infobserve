FROM python:3.8.1-slim

RUN apt-get update && \
    apt-get install apt-utils -y && \
    apt-get install yara gcc python-dev libffi-dev libssl-dev -y && \
    pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.in-project true && poetry install --no-dev

COPY . /app/

CMD . .venv/bin/activate && python main.py
