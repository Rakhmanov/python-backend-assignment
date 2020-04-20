FROM python:3.7.7-buster as base

ARG DEBIAN_FRONTEND=noninteractive

COPY ./requirements.txt .

RUN printenv

RUN apt-get update \
    && apt-get upgrade -yq \
    && apt-get install sqlite3 \
    && pip3 install -r requirements.txt
