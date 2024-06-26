#!/usr/bin/env bash

# build Hokusai in CI environment
# for use on Apple silicon MacOS

set -xeo pipefail

# install rosetta
sudo softwareupdate --install-rosetta --agree-to-license

# install x86 homebrew
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# set PATH to x86 executables
export PATH="/usr/local/bin:$PATH"

# install pyenv
brew install pyenv
echo -e '\neval "$(pyenv init --path)"' >> ~/.bash_profile

# install python pre-reqs
brew install openssl xz

# install python
arch -x86_64 pyenv install 3.10
pyenv local 3.10
pip install --upgrade pip

# install awscli
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# build hokusai
make hokusai
pyenv rehash
