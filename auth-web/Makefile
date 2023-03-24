.PHONY: setup
.PHONY: ci cd

PROJECT_NAME:=auth-web
DOCKER_NAME:=auth-web

#################################################################################
# COMMANDS -- Setup
# expects the terminal to be openshift login
# expects export OPENSHIFT_REPOSITORY=""
#################################################################################
setup: ## Clean and Install npm dependencies
	npm ci

#################################################################################
# COMMANDS - CI                                                                 #
#################################################################################
ci: lint test

lint:  ## Run linting ofcode.
	npm run lint

test:  ## Unit testing
	mv .env .env.bak
	cp .env.example .env
	npm run test:unit

#################################################################################
# COMMANDS - CD
# expects the terminal to be openshift login
# expects export OPENSHIFT_DOCKER_REGISTRY=""
# expects export OPENSHIFT_SA_NAME="$(oc whoami)"
# expects export OPENSHIFT_SA_TOKEN="$(oc whoami -t)"
# expects export OPENSHIFT_REPOSITORY=""
# expects export TAG_NAME="dev/test/prod"
#################################################################################
cd: ## CD flow
ifeq ($(TAG_NAME), test)
BUILD_TAG_NAME=test-latest
cd: build tag
else ifeq ($(TAG_NAME), prod)
BUILD_TAG_NAME=prod-latest
cd: build tag-production
else
BUILD_TAG_NAME=dev-latest
TAG_NAME=dev
cd: build tag
endif

build: ## Build the docker container
	docker build . -t $(DOCKER_NAME) \
		--build-arg VCS_REF=$(shell git rev-parse --short HEAD) \
		--build-arg BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ") \

build-nc: ## Build the docker container without caching
	docker build --no-cache -t $(DOCKER_NAME) .

REGISTRY_IMAGE=$(OPENSHIFT_DOCKER_REGISTRY)/$(OPENSHIFT_REPOSITORY)-tools/$(DOCKER_NAME)
push: #build ## Push the docker container to the registry & tag latest
	@echo "$(OPENSHIFT_SA_TOKEN)" | docker login $(OPENSHIFT_DOCKER_REGISTRY) -u $(OPENSHIFT_SA_NAME) --password-stdin ;\
    docker tag $(DOCKER_NAME) $(REGISTRY_IMAGE):$(BUILD_TAG_NAME) ;\
    docker push $(REGISTRY_IMAGE):$(BUILD_TAG_NAME)

tag: push ## tag image
	oc -n "$(OPENSHIFT_REPOSITORY)-tools" tag $(DOCKER_NAME):$(BUILD_TAG_NAME) $(DOCKER_NAME):$(TAG_NAME)

tag-production: push ## tag image
	oc -n "$(OPENSHIFT_REPOSITORY)-tools" tag $(DOCKER_NAME):$(TAG_NAME) $(DOCKER_NAME):$(TAG_NAME)-$(shell date +%F) ;\
	oc -n "$(OPENSHIFT_REPOSITORY)-tools" tag $(DOCKER_NAME):$(BUILD_TAG_NAME) $(DOCKER_NAME):$(TAG_NAME)

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################
.PHONY: help

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
