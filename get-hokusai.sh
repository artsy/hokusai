#!/bin/bash

set -e

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

TMPFILE=hokusai-$VERSION-$(uname -s)-x86_64

curl https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-$VERSION-$(uname -s)-x86_64 -o $TMPFILE
chmod +x $TMPFILE
sudo mv $TMPFILE $TARGET
