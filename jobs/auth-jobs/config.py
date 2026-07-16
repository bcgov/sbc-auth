# Copyright © 2026 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""All of the configuration for the service is captured here. All items are loaded, or have Constants defined here that are loaded into the Flask configuration. All modules and lookups get their configuration from the Flask config, rather than reading environment variables directly or by accessing this configuration directly."""

import os
import sys

from cloud_sql_connector import DBConfig
from dotenv import find_dotenv, load_dotenv

# this will load all the envars from a .env file located in the project root (jobs)
load_dotenv(find_dotenv())

CONFIGURATION = {
    "development": "config.DevConfig",
    "testing": "config.TestConfig",
    "production": "config.ProdConfig",
    "default": "config.ProdConfig",
}


def get_named_config(config_name: str = "production"):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ["production", "staging", "default"]:
        config = ProdConfig()
    elif config_name == "testing":
        config = TestConfig()
    elif config_name == "development":
        config = DevConfig()
    else:
        raise KeyError(f"Unknown configuration '{config_name}'")
    return config


class _Config:  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults for all the other configurations."""

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = "a secret"  # noqa: S105 - test configuration

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    ALEMBIC_INI = "migrations/alembic.ini"

    # POSTGRESQL
    DB_USER = os.getenv("DATABASE_USERNAME", "")
    DB_NAME = os.getenv("DATABASE_NAME", "")
    DB_SCHEMA = os.getenv("DATABASE_SCHEMA", "public")

    # Cloud SQL connector support
    DATABASE_INSTANCE_CONNECTION_NAME = os.getenv("DATABASE_INSTANCE_CONNECTION_NAME", "")
    DB_IP_TYPE = os.getenv("DATABASE_IP_TYPE", "private").lower()

    if DATABASE_INSTANCE_CONNECTION_NAME:
        SQLALCHEMY_DATABASE_URI = "postgresql+pg8000://"

        db_config = DBConfig(
            instance_name=DATABASE_INSTANCE_CONNECTION_NAME,
            database=DB_NAME,
            user=DB_USER,
            ip_type=DB_IP_TYPE,
            schema=DB_SCHEMA,
            pool_timeout=30,
            max_overflow=3,
        )

        SQLALCHEMY_ENGINE_OPTIONS = db_config.get_engine_options()
    else:
        DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
        DB_HOST = os.getenv("DATABASE_HOST", "")
        DB_PORT = os.getenv("DATABASE_PORT", "5432")
        SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # GCP PubSub
    ACCOUNT_MAILER_TOPIC = os.getenv("ACCOUNT_MAILER_TOPIC", "account-mailer-dev")

    # Account linking key notifications
    ACCOUNT_LINK_EXPIRY_REMINDER_DAYS = int(os.getenv("ACCOUNT_LINK_EXPIRY_REMINDER_DAYS", "30"))

    TESTING = False
    DEBUG = True


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """Development environment configuration."""

    TESTING = False
    DEBUG = True


class TestConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only used by the py.test suite."""

    DEBUG = True
    TESTING = True

    # POSTGRESQL
    DB_USER = os.getenv("DATABASE_TEST_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_TEST_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_TEST_NAME", "")
    DB_HOST = os.getenv("DATABASE_TEST_HOST", "")
    DB_PORT = os.getenv("DATABASE_TEST_PORT", "5432")
    _db_test_url = os.getenv("DATABASE_TEST_URL")
    if _db_test_url:
        SQLALCHEMY_DATABASE_URI = _db_test_url.replace("postgresql://", "postgresql+pg8000://", 1)
        if "+psycopg" in SQLALCHEMY_DATABASE_URI:
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("+psycopg", "+pg8000")
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"

    SERVER_NAME = "localhost:5001"


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    TESTING = False
    DEBUG = False
