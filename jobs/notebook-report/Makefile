.PHONY: clean clean-build clean-pyc clean-test ci lint test build build-nc push run setup help

CURRENT_ABS_DIR:=$(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PROJECT_NAME:=notebook-report
DOCKER_NAME:=notebook-report
VENV_DIR:=.venv

#################################################################################
# Setup                                                                         #
#################################################################################
setup: clean install ## Setup the project

install: ## Install Python dependencies in a virtual environment
	test -f $(VENV_DIR)/bin/activate || python3.12 -m venv $(VENV_DIR) ;\
	. $(VENV_DIR)/bin/activate ;\
	pip install poetry ;\
	poetry install

#################################################################################
# Clean                                                                         #
#################################################################################
clean: clean-build clean-pyc clean-test ## Clean the project
	rm -rf $(VENV_DIR)/

clean-build: ## Clean build files
	rm -fr build/ dist/ .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc: ## Clean Python cache files
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Clean test files
	find . -name '.pytest_cache' -exec rm -fr {} +
	rm -fr .tox/ .coverage htmlcov/

#################################################################################
# Linting and Testing                                                           #
#################################################################################
ci: lint test ## CI flow

lint: ## Run linting with pylint
	. $(VENV_DIR)/bin/activate && pylint --rcfile=setup.cfg src/**/*.py

test: ## Run unit tests
	. $(VENV_DIR)/bin/activate && pytest ./

#################################################################################
# Build and Push Docker                                                         #
#################################################################################
build: ## Build the Docker container
	docker build . -t $(DOCKER_NAME) \
		--build-arg VCS_REF=$(shell git rev-parse --short HEAD) \
		--build-arg BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

build-nc: ## Build the Docker container without caching
	docker build --no-cache -t $(DOCKER_NAME) .

push: build ## Push the Docker container to the registry
	@echo "$(OPENSHIFT_SA_TOKEN)" | docker login $(OPENSHIFT_DOCKER_REGISTRY) -u $(OPENSHIFT_SA_NAME) --password-stdin ;\
	docker tag $(DOCKER_NAME) $(OPENSHIFT_DOCKER_REGISTRY)/$(OPENSHIFT_REPOSITORY)-tools/$(DOCKER_NAME):latest ;\
	docker push $(OPENSHIFT_DOCKER_REGISTRY)/$(OPENSHIFT_REPOSITORY)-tools/$(DOCKER_NAME):latest

#################################################################################
# Run                                                                           #
#################################################################################
run: ## Run the project locally
	. $(VENV_DIR)/bin/activate && poetry run python notebookreport.py

#################################################################################
# Self-Documenting Commands                                                     #
#################################################################################
help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
