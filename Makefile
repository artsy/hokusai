.PHONY: dependencies test test-docker build-onefile build-onedir build-linux-docker image publish-beta publish-latest publish-version publish-pip publish-dockerhub publish-beta-dockerhub publish-github clean

AWS ?= $(shell which aws)
DOCKER_RUN ?= $(shell which docker) run --rm
GIT_PUSH ?= $(shell which git) push
GIT_TAG ?= $(shell which git) tag --sign

DIST_DIR ?= dist/
PROJECT = github.com/artsy/hokusai
VERSION ?= $(shell cat hokusai/VERSION)
MINOR_VERSION ?= $(shell cat hokusai/VERSION | awk -F"." '{ print $$1"."$$2 }')

BINARY_SUFFIX ?= -$(VERSION)-$(shell uname -s)-$(shell uname -m)

dependencies:
	pip install --upgrade pip
	pip install poetry --quiet --ignore-installed
	poetry -vvv install --no-root

tests:
	coverage run --omit="test/*" -m unittest discover test

test:
	coverage run --omit="test/*" -m unittest discover test.unit
	coverage run --omit="test/*" -m unittest discover test.smoke

integration:
	coverage run --omit="test/*" -m unittest discover test.integration

test-docker:
	$(DOCKER_RUN) \
	  --volume "$(PWD)":"/src/$(PROJECT):rw" \
	  --workdir "/src/$(PROJECT)" \
	  python:3.9.10 make dependencies test

build-onefile:
	pyinstaller \
	  --distpath=$(DIST_DIR) \
	  --workpath=/tmp/build/ \
	  hokusai_onefile.spec
	mkdir -p $(DIST_DIR)hokusai$(BINARY_SUFFIX)
	cp $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)/hokusai
	tar cfvz $(DIST_DIR)hokusai$(BINARY_SUFFIX).tar.gz -C $(DIST_DIR)hokusai$(BINARY_SUFFIX) .
	rm -rf $(DIST_DIR)hokusai$(BINARY_SUFFIX)
	mv $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)

build-onedir:
	pyinstaller \
	  --distpath=$(DIST_DIR) \
	  --workpath=/tmp/build/ \
	  hokusai_onedir.spec
	mv $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)
	tar cfvz $(DIST_DIR)hokusai$(BINARY_SUFFIX).tar.gz -C $(DIST_DIR)hokusai$(BINARY_SUFFIX) .
	rm -rf $(DIST_DIR)hokusai$(BINARY_SUFFIX)

build-linux-docker:
	$(DOCKER_RUN) \
	  --env VERSION \
	  --env DIST_DIR=/dist/ \
	  --volume "$(PWD)"/dist:/dist \
	  --volume "$(PWD)":"/src/$(PROJECT):ro" \
	  --workdir "/src/$(PROJECT)" \
	  python:3.9.10 make dependencies build

image:
	echo $(VERSION)
	docker build . \
	  --tag hokusai

publish-beta:
	$(AWS) s3 cp \
	  --acl public-read \
	  --recursive \
	  --exclude "*" \
	  --include "hokusai-beta-*" \
	  dist/ s3://artsy-provisioning-public/hokusai/

publish-latest:
	$(AWS) s3 cp \
	  --acl public-read \
	  --recursive \
	  --exclude "*" \
	  --include "hokusai-latest-*" \
	  dist/ s3://artsy-provisioning-public/hokusai/

publish-version:
	if [ "$(shell curl -I --silent https://s3.amazonaws.com/artsy-provisioning-public/hokusai/hokusai-$(BINARY_SUFFIX) --output /dev/null --write-out %{http_code})" -eq 403 ]; then \
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

publish-pip:
	pip install --upgrade wheel
	poetry build
	twine upload dist/* --verbose

publish-dockerhub:
	if [ "$(shell curl --silent https://hub.docker.com/v2/namespaces/artsy/repositories/hokusai/tags/$(VERSION) --output /dev/null --write-out %{http_code})" -eq 404 ]; then \
	  docker tag hokusai:latest artsy/hokusai:$(VERSION) && \
	  docker push artsy/hokusai:$(VERSION) && \
	  docker tag hokusai:latest artsy/hokusai:$(MINOR_VERSION) && \
	  docker push artsy/hokusai:$(MINOR_VERSION) && \
	  docker tag hokusai:latest artsy/hokusai:latest && \
	  docker push artsy/hokusai:latest; \
	else \
	  echo "Version $(VERSION) already published"; \
	  exit 1; \
	fi

publish-beta-dockerhub:
	docker tag hokusai:latest artsy/hokusai:beta
	docker push artsy/hokusai:beta

publish-github:
	$(AWS) s3 cp \
	  --acl public-read \
	  --recursive \
	  --exclude "*" \
	  --include "hokusai-$(VERSION)-*" \
	  s3://artsy-provisioning-public/hokusai/ dist/; \
	ghr \
	  --username artsy \
	  --repository hokusai \
	  --name v$(VERSION) \
	  --soft \
	  v$(VERSION) dist/

clean:
	sudo $(RM) -r ./dist
