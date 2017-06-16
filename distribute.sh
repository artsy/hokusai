#! /bin/bash

set -e

git fetch upstream --tags
git tag v$(cat hokusai/VERSION.txt)
git push upstream --tags
python setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build/ dist/ hokusai.egg-info/
