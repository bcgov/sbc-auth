[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE)
[![codecov](https://codecov.io/gh/bcgov/sbc-auth/branch/development/graph/badge.svg?flag=authapi)](https://codecov.io/gh/bcgov/sbc-auth/tree/development/auth-api)
![Auth API CHECK CI](https://github.com/bcgov/sbc-auth/workflows/Auth%20API%20CHECK%20CI/badge.svg)
![Auth API DEV CD](https://github.com/bcgov/sbc-auth/workflows/Auth%20API%20DEV%20CD/badge.svg)
![Auth API TEST CD](https://github.com/bcgov/sbc-auth/workflows/Auth%20API%20TEST%20CD/badge.svg)
# AUTH API

BC Registries authentication and authorization services.


## Development Environment

Follow the instructions of the [Development Readme](https://github.com/bcgov/entity/blob/master/docs/development.md)
to setup your local development environment.

## Development Setup

1. Follow the [instructions](https://github.com/bcgov/entity/blob/master/docs/setup-forking-workflow.md) to checkout the project from GitHub.
2. Open the auth-api directory in VS Code to treat it as a project (or WSL projec). To prevent version clashes, set up a
virtual environment to install the Python packages used by this project.
3. Run `make setup` to set up the virtual environment and install libraries.
4. Next run `pip install .` to set up the environment for running tests.

You also need to set up the variables used for environment-specific settings:
1. Copy the [dotenv template file](../docs/dotenv_template) to somewhere above the source code and rename to `.env`. You will need to fill in missing values.
   .github\workflows\auth-api-ci.yml could provide some hints for unit tests.

## Running the Auth Database on localhost

To prepare your local database:
1. In the [root project folder](../docker/docker-compose.yml): `docker-compose up -d`
2. In your `venv` environment: `python manage.py db upgrade`


Note:

**[Windows Users]**
If using WSL, may need to change the host from localhost -> <computer-name>.local
EX. in config.py and .env. 

**[Mac Users]**
: You might get an error regarding the SSL certificate verification failed.
follow the steps to resolve that issue:
1. Open the terminal window, and run **`python3 -v`** command to check the version of python.
2. run the following command:
```
pip install certifi /Applications/Python\ <version of your python>/Install\ Certificates.command
```

eg: if your python version is 3.7,
then, run

```
pip install certifi /Applications/Python\ 3.7/Install\ Certificates.command
```

## Running AUTH-API

1. Start the flask server with `(python -m flask run -p 5000)`
2. View the [OpenAPI Docs](http://127.0.0.1:5000/api/v1).

## Running Liniting

1. Run `make flake8` or `flake8 src/auth_api tests`.
2. Run `make pylint` or `pylint --rcfile=setup.cfg --disable=C0301,W0511 src/auth_api test`

## Running Unit Tests

1. Tests are run from the Status bar at the bottom of the workbench in VS Code or `pytest` command.
2. Next run `make coverage` to generate the coverage report, which appears in the *htmlcov* directory.

## Running Integration (postman) Tests

1. Start your local application(s).
2. Open postman applicaiton.
3. Import the [Integration tests environment configrations](./tests/postman/auth-api.postman_environment.json) and fill the values to match your applicaiton.
4. Import the [integration tests collection](./tests/postman/auth-api.postman_collection.json).
5. Run the collection.

## Openshift Environment

View the [document](../docs/build-deploy.md).

## Github Actions

