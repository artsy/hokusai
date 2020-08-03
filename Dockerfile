FROM python:3.5.8-alpine

WORKDIR /src

# Install Docker
RUN apk add \
      bash \
      curl \
      docker \
      git \
      openssh

# Install Docker Compose, AWS CLI
RUN pip install docker-compose==1.22.0 && \
      pip install awscli --upgrade

# Install the AWS IAM Authenticator
RUN curl -L https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.4.0/aws-iam-authenticator_0.4.0_linux_amd64 -o /usr/local/bin/aws-iam-authenticator && \
      chmod a+x /usr/local/bin/aws-iam-authenticator

COPY . /src

# Install Hokusai
RUN pip install .