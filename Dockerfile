FROM python:3.9.10-alpine

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

# Install Docker Compose, AWS CLI
RUN pip --no-cache-dir install docker-compose==1.25.5 && \
      pip --no-cache-dir install awscli --upgrade

# Install the AWS IAM Authenticator
RUN curl -L https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.4.0/aws-iam-authenticator_0.4.0_linux_amd64 -o /usr/local/bin/aws-iam-authenticator && \
      chmod a+x /usr/local/bin/aws-iam-authenticator

COPY . /src

# Install Hokusai
RUN pip install .
