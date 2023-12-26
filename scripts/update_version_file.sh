#!/usr/bin/env sh


# This script is to be run in CI only, for 'main' and 'release' branch builds.
#
# It updates hokusai/VERSION file during the builds,
# so that built artifacts have correct version numbers.
# The changes made in CI are not git committed.
#
# It also updates pyproject.toml tool.poetry.version.
#
# - 'main' build
#     Set VERSION to RELEASE_VERSION + last git commit.
#     This VERSION number signifies a beta artifact.
#
# - 'release' build
#     Set VERSION to RELEASE_VERSION.
#     This numbere signifies a cannonical artifact.
#
# hokusai/RELEASE_VERSION is manually incremented for canonical releases.
#
# hokusai/VERSION and the version number in pyproject.toml are set to dummy value in version control.


RELEASE_VERSION=v$(cat hokusai/RELEASE_VERSION)

# 'main' branch
if [ "$CIRCLE_BRANCH" = 'main' ]
then
  echo "On main branch"
  COMMIT=$(git rev-parse --short HEAD)
  VERSION="$RELEASE_VERSION-$COMMIT"
elif [ "$CIRCLE_BRANCH" = 'release' ]
then
  echo "On release branch"
  VERSION="$RELEASE_VERSION"
else
  echo "Error: not 'main' nor 'release' branch!"
  exit 1
fi

echo "Setting hokusai/VERSION to $VERSION..."
echo $VERSION > hokusai/VERSION

echo "Setting pyproject.toml tool.poetry.version to $VERSION..."
sed -i "s/999.999.999/$VERSION/" pyproject.toml
