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

1. Run `. venv/bin/activate` to change to `venv` environment.
2. Run notebook with `(python notebookreport.py)`

## Running Unit Tests

1. Run `python -m pytest` or `pytest` command.

### Important: Please remember to add run.sh permission by "git update-index --chmod=+x run.sh" before run.sh is commit to github for first time running. 
### API - can be done in VS Code
1. Login to openshift 

   ```sh
   oc login xxxxxx
   ```

2. switch to tools namespace

   ```sh
   oc project 1rdehl-tools
   ```

3. Create build image with a tag 'latest'.

   ```sh
   cd */sbc-auth/jobs/auth-notebook-report/openshift/templates
   oc create imagestream auth-notebook-report
   oc process -f auth-notebook-report-bc-template.json \
        -p GIT_REPO_URL=https://github.com/bcgov/sbc-auth.git \
    | oc apply -f -
   ```

4. Create pipeline and need to start pipeline manually.
   It will build image as a tag 'latest' and then tag it to 'dev'
   or tag it from 'dev' to 'test'
   or tag it from 'test' to 'prod'

   ```sh
   oc process -f auth-notebook-report-pipeline.json \
        -p TAG_NAME=dev \
        -p GIT_REPO_URL=https://github.com/bcgov/sbc-auth.git \
        -p WEBHOOK=github-auth-notebook-report-dev \
        -p JENKINS_FILE=./jenkins/dev.groovy \
    | oc apply -f -
   ```

### Create cron

1. Login to openshift

   ```sh
   oc login xxxxxxx
   ```

2. switch to dev namespace

   ```sh
   oc project 1rdehl-dev
   ```

3. Create cron

   ```sh
   oc process -f cron-notebook-report.yml \
        -p ENV_TAG=dev \
    | oc apply -f -
   ```
