#!/usr/bin/env sh

# This script is to be run within CircleCI only for 'release' branch builds.
# It reads the new release version from RELEASE_VERSION file and creates a Git tag for it (locally in CircleCI).
# See 'hokusai/version.py' file for more info.

RELEASE_VERSION=v$(cat RELEASE_VERSION)

# fail if not run in circleci
if [ -z "$CIRCLE_BRANCH" ]
then
  echo "Error: CIRCLE_BRANCH env var not set, is this CircleCI environment?"
  exit 1
fi

echo "On branch: $CIRCLE_BRANCH"

# fail if not 'release' branch
if [[ "$CIRCLE_BRANCH" != 'release' ]]
then
  echo "Error: not on release branch"
  exit 1
fi

# fail if RELEASE_VERSION tag already exists
release_version_tag=$(git tag -l $RELEASE_VERSION)
if [ -n "$release_version_tag" ]
then
  echo "Error: $RELEASE_VERSION tag already exists"
  exit 1
fi

# proceed with tagging
echo "Creating $RELEASE_VERSION tag"
git tag "$RELEASE_VERSION"

# tag should now exist, if not, fail
release_version_tag=$(git tag -l $RELEASE_VERSION)
if [ -z "$release_version_tag" ]
then
  echo "Error: failed to create $RELEASE_VERSION tag"
  exit 1
fi
