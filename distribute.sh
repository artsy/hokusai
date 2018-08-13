#! /bin/bash

set -e

if [ -z "$1" ]
  then
    echo "No version supplied"
fi

# Tag release

git fetch upstream --tags
git tag v$1
git push upstream --tags

# Pip package

python setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build/ dist/ hokusai.egg-info/

# Pyinstaller binary

pip install -r requirements.txt
pyinstaller hokusai.spec
s3cmd put dist/hokusai s3://artsy-provisioning-public/hokusai-v$1
s3cmd put dist/hokusai s3://artsy-provisioning-public/hokusai
rm -rf build/ dist/

# Docker image

docker login

docker build -t hokusai --build-arg HOKUSAI_VERSION=$1 .

docker tag hokusai:latest artsy/hokusai:$1
docker push artsy/hokusai:$1

docker tag hokusai:latest artsy/hokusai:latest
docker push artsy/hokusai:latest
