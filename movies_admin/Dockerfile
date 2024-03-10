FROM python:3.12-slim as python-base


ENV PYTHONUNBUFFERED=1 \
     DJANGO_SETTINGS_MODULE='config.settings' \
     VENV_DIR=/opt/venv

RUN python3 -m venv ${VENV_DIR}
ENV PATH="$VENV_DIR/bin:$PATH"

FROM python-base as python-base-updater

RUN apt-get update && apt-get install -y --no-install-recommends \
     gcc \
     gcc-12 \
    libpq-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*


RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /opt/app/staticfiles/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip

COPY movies_admin/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

FROM python-base-updater as app

COPY ./movies_admin /opt/app

WORKDIR /opt/app

RUN groupadd -r docker && useradd -d /opt/app -r -G docker app_user  \
    && chown -R app_user:app_user /opt/app && chmod 777 /opt/app -R


USER app_user
RUN newgrp docker

RUN python3 manage.py collectstatic --noinput

FROM app as django-api

COPY --from=app /opt/app /opt/app

WORKDIR /opt/app

FROM nginx:1.25.4 AS front

COPY --from=app /opt/app/staticfiles /data/static

FROM python-base-updater as etl
WORKDIR /postgres_to_es

RUN groupadd -r docker && useradd -d /postgres_to_es -r -G docker es_user  \
    && chown -R es_user:es_user /postgres_to_es && chmod 777 /postgres_to_es -R

USER es_user

COPY --chown=es_user:es_user ./postgres_to_es /postgres_to_es

FROM python-base-updater as preload-data-to-pg
WORKDIR /sqlite_to_postgres

RUN groupadd -r docker && useradd -d /sqlite_to_postgres -r -G docker preload_user  \
    && chown -R preload_user:preload_user /sqlite_to_postgres && chmod 777 /sqlite_to_postgres -R

USER preload_user

COPY --chown=preload_user:preload_user ./sqlite_to_postgres /sqlite_to_postgres
