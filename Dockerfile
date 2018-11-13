FROM python:2-alpine
ARG HOKUSAI_VERSION

# Install Docker
RUN apk add docker

# Install Docker Compose
RUN pip install docker-compose

# Install Git
RUN apk add git

# Install Hokusai
RUN pip install hokusai==$HOKUSAI_VERSION
