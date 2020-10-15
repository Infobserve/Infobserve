FROM python:3.8-slim as builder

RUN apt-get update && \
    apt-get install apt-utils -y && \
    apt-get install yara gcc python-dev libffi-dev libssl-dev -y && \
    pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.in-project true && poetry install --no-dev

FROM python:3.8-slim

WORKDIR /app

COPY --from=builder /app/.venv ./.venv/
COPY . /app/

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

CMD ["python", "main.py"]
