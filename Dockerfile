FROM python:3.10-alpine

ARG COMPOSE_VERSION=2.40.3
ARG AUTHENTICATOR_VERSION=0.7.22
# Set by BuildKit/buildx; the legacy builder leaves it empty, so RUN steps fall back to amd64
ARG TARGETARCH

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
# Compose names its assets x86_64/aarch64 rather than amd64/arm64
RUN case "${TARGETARCH:-amd64}" in amd64) COMPOSE_ARCH=x86_64 ;; arm64) COMPOSE_ARCH=aarch64 ;; *) echo "unsupported arch: ${TARGETARCH}" && exit 1 ;; esac && \
  curl -fSL https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-linux-${COMPOSE_ARCH} -o /usr/local/bin/docker-compose && \
  chmod a+x /usr/local/bin/docker-compose

# Install the AWS IAM Authenticator
RUN curl -fSL https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v${AUTHENTICATOR_VERSION}/aws-iam-authenticator_${AUTHENTICATOR_VERSION}_linux_${TARGETARCH:-amd64} -o /usr/local/bin/aws-iam-authenticator && \
      chmod a+x /usr/local/bin/aws-iam-authenticator

# Install AWS CLI
RUN pip install pip --upgrade
RUN pip --no-cache-dir install awscli --upgrade

COPY . /src

# Install Hokusai
RUN pip install --no-cache-dir .
