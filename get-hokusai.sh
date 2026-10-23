#!/bin/bash

set -e

if [ "$(uname -s)" = "Darwin" ]; then
  echo "get-hokusai.sh only supports Linux. On macOS, install with Homebrew or pip: https://github.com/artsy/hokusai#installation" >&2
  exit 1
fi

if [ "$1" ]; then
  VERSION=$1
else
  VERSION=latest
fi

if [ "$2" ]; then
  TARGET=$2
else
  TARGET=/usr/local/bin/hokusai
fi

echo "Installing Hokusai @ $VERSION to $TARGET"

curl https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-$VERSION-$(uname -s)-x86_64 -o $TARGET
chmod +x $TARGET
