FROM ubuntu:18.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install \
    git \
    procps \
    python3-dev \
    python3-pip \
    curl \
    libgdal-dev \
    vim

RUN pip3 install --upgrade pip setuptools
ADD requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /opt/worldengine
ENTRYPOINT ["python3", "worldengine"]
