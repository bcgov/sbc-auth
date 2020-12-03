.PHONY: license
.PHONY: setup
.PHONY: ci cd
.PHONY:db-update run

SHELL:=/bin/bash
MKFILE_PATH:=$(abspath $(lastword $(MAKEFILE_LIST)))
current_dir:=$(notdir $(patsubst %/,%,$(dir $(MKFILE_PATH))))
CURRENT_ABS_DIR:=$(patsubst %/,%,$(dir $(MKFILE_PATH)))

PROJECT_NAME:=auth_api

#################################################################################
# COMMANDS -- license                                                           #
#################################################################################
license: ## Verify source code license headers.
	@./scripts/verify_license_headers.sh $(CURRENT_ABS_DIR)/src $(CURRENT_ABS_DIR)/tests

#################################################################################
# COMMANDS -- Setup                                                             #
#################################################################################
setup: clean install install-dev ## Setup the project

clean: clean-build clean-pyc clean-test ## Clean the project
	@rm -rf venv/

clean-build: ## Clean build files
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Clean cache files
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## clean test files
	@find . -name '.pytest_cache' -exec rm -fr {} +
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/

install: ## Install python virtrual environment
	@rm -rf venv/
	@test -f venv/bin/activate || python3 -m venv  $(CURRENT_ABS_DIR)/venv
	@. venv/bin/activate
	@pip install --upgrade pip
	@pip install -Ur requirements/prod.txt
	@pip freeze | sort > requirements.txt
	@cat requirements/repo-libraries.txt >> requirements.txt
	@pip install -Ur requirements/repo-libraries.txt
	@pip install -Ur requirements/dev.txt
	@touch venv/bin/activate  # update so it's as new as requirements/prod.txt

install-dev: install ## Install dev environment
	@. venv/bin/activate
	@pip install -e .

#################################################################################
# COMMANDS - CI                                                                 #
#################################################################################
ci: pylint flake8 test ## CI flow

pylint: ## Linting with pylint
	@. venv/bin/activate
	@pylint --rcfile=setup.cfg  src/$(PROJECT_NAME)

flake8: ## Linting with flake8
	@. venv/bin/activate
	@flake8 src/$(PROJECT_NAME) tests

test: ## Unit testing
	@. venv/bin/activate
	@pytest

mac-cov: local-test ## Run the coverage report and display in a browser window
	@open -a "Google Chrome" htmlcov/index.html

#################################################################################
# COMMANDS - CD                                                               #
#################################################################################
cd: build ## CD flow

build: ## Build the docker container
	@docker build -t $(PROJECT_NAME) .

build-nc: ## Build the docker container without caching
	@docker build --no-cache -t $(PROJECT_NAME) .

#################################################################################
# COMMANDS - Local                                                              #
#################################################################################

run: db-update ## Run the project in local
	@. venv/bin/activate
	@python -m flask run -p 5000

db-update: ## Update the local database
	@. venv/bin/activate
	@python -m manage.py db upgrade


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################
.PHONY: help

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
