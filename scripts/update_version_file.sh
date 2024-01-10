#!/usr/bin/env sh

# Set Hokusai version in:
#
# - hokusai/VERSION file
#     'hokusai version' command retrieves version from this file.
#
# - pyproject.toml file tool.poetry.version field
#     This field decides the version number in artifact file names, and in PyPI.
#
# Set version differently depending on environment and Git branch.
#
# For 'release' branch build in CircleCI, set version to what is in hokusai/RELEASE_VERSION file.
#
# For all others, set it to:
#   - hokusai/RELEASE_VERSION, plus
#   - git rev-parse --short HEAD
# For example, if RELEASE_VERSION is 2.0.0 and git rev-parse is 680c2ad, set version to 2.0.0+680c2ad
# This is useful for identifying Beta builds.

RELEASE_VERSION=$(cat hokusai/RELEASE_VERSION)

if [ "$CIRCLE_BRANCH" = 'release' ]
then
  echo "In CircleCI 'release' branch build."
  VERSION="$RELEASE_VERSION"
else
  echo "In CircleCI non-release branch build, or not even in CircleCI."
  COMMIT=$(git rev-parse --short HEAD)
  VERSION="$RELEASE_VERSION+$COMMIT"
fi

echo "Setting $VERSION in hokusai/VERSION file..."
echo $VERSION > hokusai/VERSION

echo "Setting $VERSION in pyproject.toml file tool.poetry.version field..."
# use -i.bak so it works with CircleCI Mac's sed
sed -i.bak "s/999\.999\.999/$VERSION/" pyproject.toml
