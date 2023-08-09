FROM python:3.9.10-alpine

ARG COMPOSE_VERSION=2.17.2
ARG AUTHENTICATOR_VERSION=0.4.0

WORKDIR /src

# Install Docker
RUN apk add --no-cache \
      bash \
      build-base \
      curl \
      docker-cli \
      git \
      jq \
      libffi-dev \
      openssh \
      openssl-dev

# Install Docker Compose
RUN curl -SL https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose && \
  chmod a+x /usr/local/bin/docker-compose

# Install the AWS IAM Authenticator
RUN curl -SL https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v${AUTHENTICATOR_VERSION}/aws-iam-authenticator_${AUTHENTICATOR_VERSION}_linux_amd64 -o /usr/local/bin/aws-iam-authenticator && \
      chmod a+x /usr/local/bin/aws-iam-authenticator

# Install AWS CLI
RUN pip --no-cache-dir install awscli --upgrade

COPY . /src

# Install Hokusai
RUN pip install --no-cache-dir .
