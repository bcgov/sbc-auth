# Visual Studio Code

> Setup Python API development environment in VSCODE Windows 10.

## [VS Code](https://code.visualstudio.com) Tips and Tricks

> The content is now at [vscode-docs](https://github.com/Microsoft/vscode-docs/blob/master/docs/getstarted/tips-and-tricks.md).

## [VS CODE] Plugin

    Python
    PostgreSQL
    GitLens
    Docker
    Code Spell Checker
    autoDocstring

## Checkout Source Code

> See developer.github.md

## Create Python Virtual Environment

    Windows:

    ```sh
    cd $workspace_dir/sbc-auth/auth-api
    python -m venv venv
    venv/Scripts/activate
    python -m pip install --upgrade pip setuptools

    pip install flake8 pylint pytest coverage pytest-cov
    pip install -r requirements/prod.txt
    pip install -r requirements/dev.txt
    pip install -r requirements/repo-libraries.txt
    ```

    Mac or Linux:
    ```sh
    cd $workspace_dir/sbc-auth/auth-api
    make setup
    ```

## [VS CODE] workspace auth-api.code-workspace

    ```json
    {
        "folders": [
        {
            "path": "."
        }
        ],
        "settings": {
            "workbench.colorCustomizations": {
                "activityBar.background": "#3B107B",
                "titleBar.activeBackground": "#5216AC",
                "titleBar.activeForeground": "#FDFCFF"
            },
            "python.autoComplete.addBrackets": true,
            "python.autoComplete.extraPaths": ["${workspaceRoot}/src"],

            "files.exclude": {
                // exclude python & pytest cache dirs
                ".pytest_cache": true,
                "**/__pycache__": true,
                ".cache": true,
                "allure": true,
                ".idea": true,
                "node_modules": true
            },

            "python.workspaceSymbols.exclusionPatterns": [
                "**/.env/",
                "**/site-packages/**",
                "_build",
                "**/.idea/"
            ],
            "python.analysis.logLevel": "Warning"
        }
    }

    ```

## [VS CODE] project settings.json

    ```json
    {
        "python.testing.autoTestDiscoverOnSaveEnabled": true,
        "python.autoComplete.extraPaths": ["${workspaceRoot}/src"],
        "python.pythonPath": "${workspaceRoot}/venv/Scripts/python.exe",
        "python.envFile": "${workspaceFolder}/.env}",
        "python.linting.pylintEnabled": true,
        "python.linting.flake8Enabled": false,
        "python.linting.enabled": true,
        "python.linting.pylintArgs": [
            "--rcfile=setup.cfg",
            "--load-plugins=pylint_flask",
            "--disable=C0301,W0511"
        ],
        "python.linting.flake8Args": ["--rcfile=setup.cfg"],
        "python.testing.pyTestArgs": [],
        "python.testing.unittestEnabled": false,
        "python.testing.nosetestsEnabled": false,
        "python.testing.pyTestEnabled": true
    }

    ```

## [VS CODE] User settings.json

    Add following setting into User settings.json

    ```json
    "terminal.integrated.env.windows": { "PYTHONPATH": "./src/" }
    ```

## [VS CODE] Python Interpreter

    Ctrl + Shift + P and `Python: Select Interpreter`

## [VS CODE] Run API

    Create Task (Terminal -> Configure Default Build Task)

    ```json
    {
        // See https://go.microsoft.com/fwlink/?LinkId=733558
        // for the documentation about the tasks.json format
        "version": "2.0.0",
        "tasks": [
            {
            "label": "Run Debug Server",
            "type": "shell",
            "command": "${workspaceRoot}/venv/Scripts/flask run -p 5000",
            "group": {
                "kind": "build",
                "isDefault": true
            }
            }
        ]
    }

    ```

## [VS CODE] Debug API

    Modify launch.json (Ctrl + Shift + D)

    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
            "name": "Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "PYTHONPATH": "src",
                "FLASK_APP": "wsgi.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "0"
            },
            "args": ["run", "--no-debugger", "--no-reload"],
            "jinja": true
            }
        ]
    }
    ```

## [VS CODE] Run commands

    Ctrl + Shift + `

    Windows:

    ```sh
    flake8 src/auth-api tests
    pytest
    coverage run -m pytest
    coverage report
    start chrome htmlcov/index.html
    ```

    Mac or Linux:

    ```sh
    make flake8
    make pylint
    make local-test
    make local-coverage
    make mac-cov
    ```
