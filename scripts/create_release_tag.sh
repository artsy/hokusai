#!/usr/bin/env bash

RELEASE_VERSION=$(cat VERSION)

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "On branch: $CURRENT_BRANCH"

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
