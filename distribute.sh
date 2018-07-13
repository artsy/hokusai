#! /bin/bash

set -e

# Tag release

git fetch upstream --tags
git tag v$(python -c 'from hokusai.version import VERSION; print(VERSION)')
git push upstream --tags

# Pip package

python setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build/ dist/ hokusai.egg-info/

# Pyinstaller binary

pip install -r requirements.txt
pyinstaller hokusai.spec
s3cmd put dist/hokusai s3://artsy-provisioning-public/hokusai-v$(python -c 'from hokusai.version import VERSION; print(VERSION)')
s3cmd put dist/hokusai s3://artsy-provisioning-public/hokusai
rm -rf build/ dist/

# Docker image

docker login

docker build -t hokusai --build-arg HOKUSAI_VERSION=$(python -c 'from hokusai.version import VERSION; print(VERSION)') .

docker tag hokusai:latest artsy/hokusai:$(python -c 'from hokusai.version import VERSION; print(VERSION)')
docker push artsy/hokusai:$(python -c 'from hokusai.version import VERSION; print(VERSION)')

docker tag hokusai:latest artsy/hokusai:latest
docker push artsy/hokusai:latest
