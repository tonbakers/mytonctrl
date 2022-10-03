FROM python:3.8 AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --upgrade pip pip-tools \
    && pip install poetry \
    && apt-get autoremove -y \
    && python -m venv /venv

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.13

COPY pyproject.toml poetry.lock ./
RUN touch requirements.in \
    && poetry export -f requirements.txt \
    && pip-compile --generate-hashes requirements.in \
    && pip install -r requirements.txt
COPY . .

FROM builder AS final

COPY --from=builder /venv /venv
COPY . /app
RUN . /venv/bin/activate
CMD ["uvicorn", "--loop", "uvloop", "--workers", "5", "src.validator_stats.app:app"]
