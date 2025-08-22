FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry \
    && apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

COPY . .

ARG SECRET_KEY="django-insecure-default"
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE="config.settings"

RUN mkdir -p /app/media

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn config.wsgi:application --build 0.0.0.0:8000"]