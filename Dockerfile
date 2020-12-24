FROM python:3.9

WORKDIR /wswp

RUN pip install pipenv

COPY . .

RUN pipenv install --system