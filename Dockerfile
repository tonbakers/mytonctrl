FROM python:3.8 AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --upgrade pip \
    && pip install poetry \
    && apt-get autoremove -y

FROM builder
COPY . /app

RUN cd /app && poetry install -n --no-ansi \
    && poetry lock --no-update

WORKDIR /app

CMD ["poetry", "run", "python", "validator_node_exporter.py"]
