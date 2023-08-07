FROM python:3.9.17-slim-bookworm

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && useradd -u 4200 wswp

WORKDIR /wswp

COPY requirements.txt /wswp/requirements.txt

RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install -r requirements.txt \
    && chown -R wswp:wswp /wswp

COPY . /wswp

USER wswp

CMD . /opt/venv/bin/activate && exec gunicorn -w 1 -b :8000 "src:create_app('src.config.ProdConfig')"

EXPOSE 8000