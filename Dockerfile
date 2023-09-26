FROM python:3.10-slim as builder

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install apt-utils -y && \
    apt-get install yara gcc python3-dev libffi-dev libssl-dev -y && \
    pip install --upgrade pip && \
    pip install poetry wheel

WORKDIR /app

COPY pyproject.toml /app/
RUN poetry config virtualenvs.in-project true && poetry install --only-main

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /app/.venv ./.venv/
COPY . /app/

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

CMD ["python", "main.py"]
