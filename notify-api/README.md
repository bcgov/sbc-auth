[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=bcgov_sbc-auth&metric=alert_status)](https://sonarcloud.io/code?id=bcgov_sbc-auth&selected=bcgov_sbc-auth%3Anotify-api)
[![codecov](https://codecov.io/gh/bcgov/sbc-auth/branch/master/graph/badge.svg)](https://codecov.io/gh/bcgov/sbc-auth)

# Notify API

BC Registries notify services.


## Development Environment

Following the instructions of the [Development Readme](https://github.com/bcgov/entity/blob/master/docs/development.md)
to setup your local development environment.

## Development Setup

1. Follow the [instructions](https://github.com/bcgov/entity/blob/master/docs/setup-forking-workflow.md) to checkout the project from GitHub.
2. Open the notify-api directory in VS Code to treat it as a project (or WSL projec). To prevent version clashes, set up a
virtual environment to install the Python packages used by this project.
3. Run `make setup` to set up the virtual environment and install libraries.
4. Next run `pip install .` to set up the environment for running tests.

You also need to set up the variables used for environment-specific settings:
1. Copy the [dotenv template file](./docs/dotenv_template) to somewhere above the source code and rename to `.env`. You will need to fill in missing values.

## Running the Auth Database on localhost

To prepare your local database:
1. In the [root project folder](../docker/docker-compose.yml): `docker-compose up -d`
2. In your `venv` environment: `alembic db upgrade`

## Running NOTIFY-API

1. Start the flask server with `(uvicorn main:app --reload --port 5000)`
2. View the [OpenAPI Docs](http://127.0.0.1:5000/docs).

## Running Liniting

1. Run `make flake8` or `flake8 src/auth_api tests`.
2. Run `make pylint` or `pylint --rcfile=setup.cfg --disable=C0301,W0511 src/auth_api test`

## Running Unit Tests

1. Tests are run from the Status bar at the bottom of the workbench in VS Code or `pytest` command.
2. Next run `make coverage` to generate the coverage report, which appears in the *htmlcov* directory.

## Openshift Environment

View the [document](../docs/build-deploy.md).
