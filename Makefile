.PHONY: dependencies test test-docker build build-linux-docker publish-head publish-latest publish-version tag clean release

AWS ?= $(shell which aws)
DOCKER_RUN ?= $(shell which docker) run --rm
GIT_PUSH ?= $(shell which git) push
GIT_TAG ?= $(shell which git) tag --sign

DIST_DIR ?= dist/
PROJECT = github.com/artsy/hokusai
VERSION ?= $(shell cat hokusai/VERSION)

dependencies:
	pip install --requirement requirements.txt --quiet
	pip install --quiet pyinstaller

test:
	python -m unittest discover test

build: BINARY_SUFFIX ?= -$(VERSION)-$(shell uname -s)-$(shell uname -m)
build:
	pyinstaller \
	  --distpath=$(DIST_DIR) \
	  --workpath=/tmp/build/ \
	  hokusai.spec
	mv $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)

test-docker:
	$(DOCKER_RUN) \
	  --volume "$(PWD)":"/src/$(PROJECT):ro" \
	  --workdir "/src/$(PROJECT)" \
	  python:2 make install-dependencies test

build-linux-docker:
	$(DOCKER_RUN) \
	  --env VERSION \
	  --env DIST_DIR=/dist/ \
	  --volume "$(PWD)"/dist:/dist \
	  --volume "$(PWD)":"/src/$(PROJECT):ro" \
	  --workdir "/src/$(PROJECT)" \
	  python:2 make install-dependencies build

publish-head:
	$(AWS) s3 cp \
	  --acl public-read \
	  --recursive \
	  --exclude "*" \
	  --include "hokusai-head-*" \
	  dist/ s3://artsy-provisioning-public/hokusai/

publish-latest:
	$(AWS) s3 cp \
	  --acl public-read \
	  --recursive \
	  --exclude "*" \
	  --include "hokusai-latest-*" \
	  dist/ s3://artsy-provisioning-public/hokusai/

publish-version:
	if [ "$(shell curl https://s3.amazonaws.com/artsy-provisioning-public/hokusai/hokusai-$(VERSION)-linux-amd64 --output /dev/null --write-out %{http_code})" -eq 403 ]; then \
	  $(AWS) s3 cp \
	    --acl public-read \
	    --recursive \
	    --exclude "*" \
	    --include "hokusai-$(VERSION)-*" \
	    dist/ s3://artsy-provisioning-public/hokusai/; \
	else \
	  echo "Version $(VERSION) already published"; \
	  exit 1; \
	fi

tag:
	$(GIT_TAG) --message v$(VERSION) v$(VERSION)
	$(GIT_PUSH) origin refs/tags/v$(VERSION)

clean:
	sudo $(RM) -r ./dist

# This must be run on an OS X machine as the OS X binary is built natively.
release:
	$(MAKE) build-docker-linux
	$(MAKE) build
	$(MAKE) build-docker-linux VERSION=latest
	$(MAKE) build VERSION=latest
	$(MAKE) publish-version
	$(MAKE) publish-latest
	$(MAKE) tag
