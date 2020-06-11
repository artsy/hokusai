#!/bin/bash

# Use: ./release-homebrew.sh
#
# Requires git, wget, shasum, awk and a ssh Github deploy key with write access
#

VERSION=$(cat ./hokusai/VERSION)

cd /tmp

wget https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-$VERSION-Darwin-x86_64.tar.gz
SHA256=$(shasum -a 256 hokusai-$VERSION-Darwin-x86_64.tar.gz | awk '{ print $1 }')
rm hokusai-$VERSION-Darwin-x86_64.tar.gz

git clone git@github.com:artsy/homebrew-formulas.git
cd ./homebrew-formulas

cat <<EOF > ./Formula/hokusai.rb
class Hokusai < Formula
  desc 'Hokusai is a Docker + Kubernetes CLI for application developers'
  homepage 'https://github.com/artsy/hokusai'
  url 'https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-$VERSION-Darwin-x86_64.tar.gz'
  sha256 '$SHA256'
  version '$VERSION'

  def install
    bin.install 'hokusai'
  end
end
EOF

git commit -am "Release Hokusai $VERSION"
git push origin master

cd /tmp
rm -rf ./homebrew-formulas
