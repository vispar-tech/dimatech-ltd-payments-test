FROM python:3.12-slim

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=2.3.2

WORKDIR /usr/src/
COPY ./app ./app
COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry install --only main

CMD ["python", "-m", "app"]
