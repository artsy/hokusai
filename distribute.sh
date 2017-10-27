#! /bin/bash

set -e

# Tag release

git fetch upstream --tags
git tag v$(cat hokusai/VERSION.txt)
git push upstream --tags

# Pip package

python setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build/ dist/ hokusai.egg-info/

# Docker image

docker login

docker build -t hokusai .

docker tag hokusai:latest artsy/hokusai:$(cat hokusai/VERSION.txt)
docker push artsy/hokusai:$(cat hokusai/VERSION.txt)

docker tag hokusai:latest artsy/hokusai:latest
docker push artsy/hokusai:latest
