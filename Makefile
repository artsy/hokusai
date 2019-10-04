.PHONY: dependencies test test-docker build build-linux-docker image publish-head publish-latest publish-version publish-pip publish-dockerhub publish-head-dockerhub publish-github clean

AWS ?= $(shell which aws)
DOCKER_RUN ?= $(shell which docker) run --rm
GIT_PUSH ?= $(shell which git) push
GIT_TAG ?= $(shell which git) tag --sign

DIST_DIR ?= dist/
PROJECT = github.com/artsy/hokusai
VERSION ?= $(shell cat hokusai/VERSION)
MINOR_VERSION ?= $(shell cat hokusai/VERSION | awk -F"." '{ print $$1"."$$2 }')

dependencies:
	pip install pipenv --quiet --ignore-installed
	pipenv install --deploy
	pip install --quiet pyinstaller==3.3.1

test:
	pipenv run unit-tests

integration:
	pipenv run integration-tests

test-docker:
	$(DOCKER_RUN) \
	  --volume "$(PWD)":"/src/$(PROJECT):ro" \
	  --workdir "/src/$(PROJECT)" \
	  python:2 make dependencies test

build: BINARY_SUFFIX ?= -$(VERSION)-$(shell uname -s)-$(shell uname -m)
build:
	pyinstaller \
	  --distpath=$(DIST_DIR) \
	  --workpath=/tmp/build/ \
	  hokusai.spec
	mkdir -p $(DIST_DIR)hokusai$(BINARY_SUFFIX)
	cp $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)/hokusai
	tar cfvz $(DIST_DIR)hokusai$(BINARY_SUFFIX).tar.gz -C $(DIST_DIR)hokusai$(BINARY_SUFFIX) .
	rm -rf $(DIST_DIR)hokusai$(BINARY_SUFFIX)
	mv $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)

build-linux-docker:
	$(DOCKER_RUN) \
	  --env VERSION \
	  --env DIST_DIR=/dist/ \
	  --volume "$(PWD)"/dist:/dist \
	  --volume "$(PWD)":"/src/$(PROJECT):ro" \
	  --workdir "/src/$(PROJECT)" \
	  python:2 make dependencies build

image:
	echo $(VERSION)
	docker build . \
	  --tag hokusai

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
	if [ "$(shell curl --silent https://s3.amazonaws.com/artsy-provisioning-public/hokusai/hokusai-$(VERSION)-linux-amd64 --output /dev/null --write-out %{http_code})" -eq 403 ]; then \
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
	python setup.py sdist bdist_wheel
	twine upload dist/*

publish-dockerhub:
	if [ "$(shell curl --silent https://index.docker.io/v1/repositories/artsy/hokusai/tags/$(VERSION) --output /dev/null --write-out %{http_code})" -eq 404 ]; then \
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

publish-head-dockerhub:
	docker tag hokusai:latest artsy/hokusai:head
	docker push artsy/hokusai:head

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
