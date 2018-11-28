FROM python:2-alpine

# Install Docker
RUN apk add docker

# Install Docker Compose
RUN pip install docker-compose==1.22.0

# Install Git and Ssh
RUN apk add git openssh

ADD . /src
WORKDIR /src

# Install Hokusai
RUN pip install .
