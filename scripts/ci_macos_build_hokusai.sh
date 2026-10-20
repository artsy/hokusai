#!/usr/bin/env bash

# build Hokusai in CI environment
# for use on Apple silicon MacOS

set -xeo pipefail

# install pyenv and python pre-reqs
time brew install pyenv openssl xz
echo -e '\neval "$(pyenv init --path)"' >> ~/.bash_profile
eval "$(pyenv init --path)"

# install python
export PYTHON_BUILD_CURL_OPTS="--retry 3 --retry-connrefused --retry-delay 5"
time pyenv install 3.10
pyenv local 3.10
time pip install --upgrade pip

# install awscli
time curl --retry 3 --retry-connrefused --retry-delay 5 "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
time sudo installer -pkg AWSCLIV2.pkg -target /

# build hokusai
time make hokusai
pyenv rehash
