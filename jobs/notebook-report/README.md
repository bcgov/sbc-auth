# Notebook Report

Generate notebook report

## Development Environment

Follow the instructions of the [Development Readme](https://github.com/bcgov/entity/blob/master/docs/development.md)
to setup your local development environment.

## Development Setup

1. Follow the [instructions](https://github.com/bcgov/entity/blob/master/docs/setup-forking-workflow.md) to checkout the project from GitHub.
2. Open the notebook-report directory in VS Code to treat it as a project (or WSL projec). To prevent version clashes, set up a virtual environment to install the Python packages used by this project.
3. Run `make setup` to set up the virtual environment and install libraries.

## Running Notebook Report

1. Run 'make setup' to set up the virtual environment and install libraries.
2. Run 'eval $(poetry env activate)' to change to .venv environment.
3. Keep .env file under notebook-report directory
4. Run 'cd src'.
5. Run notebook with poetry by 'python notebookreport.py' in src directory or './run.sh' in notebook-report directory.