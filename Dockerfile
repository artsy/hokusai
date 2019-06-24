FROM python:2-alpine

# Install Docker
RUN apk add docker curl

# Install Docker Compose
RUN pip install docker-compose==1.22.0

# Install the AWS CLI
RUN pip install awscli --upgrade

# Install Git, Ssh, and bash
RUN apk add git openssh bash

# Install the AWS IAM Authenticator
RUN curl -L https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.4.0/aws-iam-authenticator_0.4.0_linux_amd64 -o /usr/local/bin/aws-iam-authenticator && chmod a+x /usr/local/bin/aws-iam-authenticator

ADD . /src
WORKDIR /src

# Install Hokusai
RUN pip install .
