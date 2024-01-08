.PHONY: dependencies test integration pyinstaller-build-onefile pyinstaller-build-onedir publish-to-s3 publish-to-s3-canonical build-docker-image publish-to-dockerhub-beta publish-to-dockerhub-canonical-and-latest publish-to-pip publish-to-github clean

# a var passed in as an argument to 'make' command moots its ?= assgiment
AWS ?= $(shell which aws)
DIST_DIR ?= dist/
PROJECT = github.com/artsy/hokusai
VERSION ?= $(shell cat hokusai/VERSION)
MINOR_VERSION ?= $(shell cat hokusai/VERSION | awk -F"." '{ print $$1"."$$2 }')
RELEASE_MINOR_VERSION ?= $(shell cat hokusai/VERSION | awk -F"." '{ print $$1"."$$2 }')
ARTIFACT_LABEL ?= $(shell cat hokusai/VERSION)
BINARY_SUFFIX ?= -$(ARTIFACT_LABEL)-$(shell uname -s)-$(shell uname -m)

dependencies:
	pip install --upgrade pip
	# pin version due to https://github.com/python-poetry/poetry/issues/7184
	pip install poetry==1.2.2 --quiet --ignore-installed
	poetry --version
	poetry install --no-root

test:
	coverage run -m pytest test/unit
	coverage run --omit="test/*" -m unittest discover test.smoke

integration:
	coverage run -m pytest test/integration

pyinstaller-build-onefile: # for linux
	pyinstaller \
	  --distpath=$(DIST_DIR) \
	  --workpath=/tmp/build/ \
	  hokusai_onefile.spec
	mkdir -p $(DIST_DIR)hokusai$(BINARY_SUFFIX)
	cp $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)/hokusai
	tar cfvz $(DIST_DIR)hokusai$(BINARY_SUFFIX).tar.gz -C $(DIST_DIR)hokusai$(BINARY_SUFFIX) .
	rm -rf $(DIST_DIR)hokusai$(BINARY_SUFFIX)
	mv $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)

# for mac (because build-onefile's binary runs too slow on mac)
pyinstaller-build-onedir:
	pyinstaller \
	  --distpath=$(DIST_DIR) \
	  --workpath=/tmp/build/ \
	  hokusai_onedir.spec
	mv $(DIST_DIR)hokusai $(DIST_DIR)hokusai$(BINARY_SUFFIX)
	tar cfvz $(DIST_DIR)hokusai$(BINARY_SUFFIX).tar.gz -C $(DIST_DIR)hokusai$(BINARY_SUFFIX) .
	rm -rf $(DIST_DIR)hokusai$(BINARY_SUFFIX)

publish-to-s3: # for 'beta' and 'latest'
	$(AWS) s3 cp \
	  --acl public-read \
	  --recursive \
	  --exclude "*" \
	  --include "hokusai-$(ARTIFACT_LABEL)-*" \
	  dist/ s3://artsy-provisioning-public/hokusai/

publish-to-s3-canonical:
	if [ "$(shell curl -I --silent https://s3.amazonaws.com/artsy-provisioning-public/hokusai/hokusai-$(BINARY_SUFFIX) --output /dev/null --write-out %{http_code})" -eq 403 ]; then \
	  $(AWS) s3 cp \
	    --acl public-read \
	    --recursive \
	    --exclude "*" \
	    --include "hokusai-$(ARTIFACT_LABEL)-*" \
	    dist/ s3://artsy-provisioning-public/hokusai/; \
	else \
	  echo "Version $(ARTIFACT_LABEL) already published"; \
	  exit 1; \
	fi

build-docker-image:
	poetry build
	docker build . \
	  --tag hokusai

publish-to-dockerhub-beta:
	docker tag hokusai:latest artsy/hokusai:beta
	docker push artsy/hokusai:beta

publish-to-dockerhub-canonical-and-latest:
	if [ "$(shell curl --silent https://hub.docker.com/v2/namespaces/artsy/repositories/hokusai/tags/$(ARTIFACT_LABEL) --output /dev/null --write-out %{http_code})" -eq 404 ]; then \
	  docker tag hokusai:latest artsy/hokusai:$(ARTIFACT_LABEL) && \
	  docker push artsy/hokusai:$(ARTIFACT_LABEL) && \
	  docker tag hokusai:latest artsy/hokusai:$(RELEASE_MINOR_VERSION) && \
	  docker push artsy/hokusai:$(RELEASE_MINOR_VERSION) && \
	  docker tag hokusai:latest artsy/hokusai:latest && \
	  docker push artsy/hokusai:latest; \
	else \
	  echo "Version $(ARTIFACT_LABEL) already published"; \
	  exit 1; \
	fi

publish-to-pip:
	pip install --upgrade wheel
	poetry version $(RELEASE_VERSION) # bump version in pyproject.toml
	poetry build
	twine upload dist/* --verbose

publish-to-github:
	$(AWS) s3 cp \
	  --acl public-read \
	  --recursive \
	  --exclude "*" \
	  --include "hokusai-$(ARTIFACT_LABEL)-*" \
	  s3://artsy-provisioning-public/hokusai/ dist/; \
	ghr \
	  --username artsy \
	  --repository hokusai \
	  --name v$(ARTIFACT_LABEL) \
	  --soft \
	  v$(ARTIFACT_LABEL) dist/

clean:
	sudo $(RM) -r ./dist
