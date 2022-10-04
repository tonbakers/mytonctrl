FROM python:3.8 AS builder
ENV PYTHONUNBUFFERED=true
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app
COPY . .
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --upgrade pip \
    && pip install poetry \
    && poetry export --without-hashes \
      --format requirements.txt --output requirements.txt \
    && pip install -r requirements.txt \
    && apt-get autoremove -y

EXPOSE 5561
CMD ["python", "-m", "uvicorn", "--loop", "uvloop", "--workers", "5", "src.validator_stats.app:app"]
