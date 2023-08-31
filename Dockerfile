FROM debian:stretch

RUN apt-get update && \
    apt-get -y install git \
    procps \
    python-dev \
    python-pip \
    curl \
    vim

RUN pip install --upgrade pip setuptools

WORKDIR /app
ADD . /app

RUN pip install -r /app/requirements-dev.txt


