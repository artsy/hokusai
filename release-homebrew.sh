#!/bin/bash

# Use: ./release-homebrew.sh
#
# Requires git, wget, shasum, awk, grep and a ssh Github deploy key with write access to git@github.com:artsy/homebrew-formulas.git
#

set -e

VERSION=$(cat ./hokusai/VERSION)

cd /tmp

wget https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-$VERSION-Darwin-x86_64.tar.gz

UNAME=$(uname)
if [ $UNAME == "Darwin" ]; then
  SHA256=$(shasum -a 256 hokusai-$VERSION-Darwin-x86_64.tar.gz | awk '{ print $1 }')
fi

if [ $UNAME == "Linux" ]; then
  SHA256=$(sha256sum hokusai-$VERSION-Darwin-x86_64.tar.gz | awk '{ print $1 }')
fi

rm hokusai-$VERSION-Darwin-x86_64.tar.gz

git clone git@github.com:artsy/homebrew-formulas.git
cd ./homebrew-formulas

if grep $VERSION ./Formula/hokusai.rb; then
  echo "Formula version already set to $VERSION"
  cd /tmp
  rm -rf ./homebrew-formulas
  exit 0
fi

echo "Bumping formula version to $VERSION"

cat <<EOF > ./Formula/hokusai.rb
class Hokusai < Formula
  desc 'Hokusai is a Docker + Kubernetes CLI for application developers'
  homepage 'https://github.com/artsy/hokusai'
  url 'https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-$VERSION-Darwin-x86_64.tar.gz'
  sha256 '$SHA256'
  versionz '$VERSION'

  def install
    bin.install 'hokusai'
  end
end
EOF

git commit --author="Hokusai CI" -a -m "Release Hokusai $VERSION"
git push origin master

cd /tmp
rm -rf ./homebrew-formulas
