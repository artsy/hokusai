#! /bin/bash

set -e

git fetch upstream --tags
git tag v$(cat hokusai/VERSION.txt)
git push upstream --tags
python setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build/ dist/ hokusai.egg-info/

docker login

docker build -t hokusai .

docker tag hokusai:$(cat hokusai/VERSION.txt) artsy/hokusai:$(cat hokusai/VERSION.txt)
docker push artsy/hokusai:$(cat hokusai/VERSION.txt)

docker tag hokusai:latest artsy/hokusai:latest
docker push artsy/hokusai:latest
