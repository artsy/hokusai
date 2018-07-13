FROM python:2
ARG HOKUSAI_VERSION

# Install Docker
RUN apt-get update
RUN apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
RUN curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") $(lsb_release -cs) stable"
RUN apt-get update
RUN apt-get install -y docker-ce

# Install Docker Compose
RUN pip install docker-compose

# Install Git
RUN apt-get install -y git

# Install Hokusai
RUN pip install hokusai==$HOKUSAI_VERSION
