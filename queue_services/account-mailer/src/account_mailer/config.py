# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""All of the configuration for the service is captured here.

All items are loaded, or have Constants defined here that
are loaded into the Flask configuration.
All modules and lookups get their configuration from the
Flask config, rather than reading environment variables directly
or by accessing this configuration directly.
"""
import os
import random

from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

CONFIGURATION = {
    'development': 'account_mailer.config.DevConfig',
    'testing': 'account_mailer.config.TestConfig',
    'production': 'account_mailer.config.ProdConfig',
    'default': 'account_mailer.config.ProdConfig'
}


def get_named_config(config_name: str = 'production'):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ['production', 'staging', 'default']:
        app_config = ProdConfig()
    elif config_name == 'testing':
        app_config = TestConfig()
    elif config_name == 'development':
        app_config = DevConfig()
    else:
        raise KeyError(f'Unknown configuration: {config_name}')
    return app_config


class _Config():  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SENTRY_DSN = os.getenv('SENTRY_DSN', None)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_NAME', '')
    DB_HOST = os.getenv('DATABASE_HOST', '')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        name=DB_NAME,
    )

    # Service account details
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('KEYCLOAK_SERVICE_ACCOUNT_ID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('KEYCLOAK_SERVICE_ACCOUNT_SECRET')

    # pay-API URL
    PAY_API_URL = os.getenv('PAY_API_URL')

    # notify-API URL
    NOTIFY_API_URL = os.getenv('NOTIFY_API_URL')

    # REPORT API Settings
    REPORT_API_BASE_URL = os.getenv('REPORT_API_BASE_URL')

    NATS_CONNECTION_OPTIONS = {
        'servers': os.getenv('NATS_SERVERS', 'nats://127.0.0.1:4222').split(','),
        'name': os.getenv('NATS_MAILER_CLIENT_NAME', 'account.mailer.worker')
    }
    STAN_CONNECTION_OPTIONS = {
        'cluster_id': os.getenv('NATS_CLUSTER_ID', 'test-cluster'),
        'client_id': str(random.SystemRandom().getrandbits(0x58)),
        'ping_interval': 1,
        'ping_max_out': 5,
    }

    SUBSCRIPTION_OPTIONS = {
        'subject': os.getenv('NATS_MAILER_SUBJECT', 'account.mailer'),
        'queue': os.getenv('NATS_MAILER_QUEUE', 'account.mailer.worker'),
        'durable_name': os.getenv('NATS_MAILER_QUEUE', 'account-mailer-worker') + '_durable',
    }

    REFUND_REQUEST = {
        'recipients': os.getenv('REFUND_REQUEST_RECIPIENTS', ''),
    }

    PDF_TEMPLATE_PATH = os.getenv('PDF_TEMPLATE_PATH', 'src/account_mailer/pdf_templates')

    TEMPLATE_PATH = os.getenv('TEMPLATE_PATH', 'src/account_mailer/email_templates')

    HTTP_ORIGIN = os.getenv('HTTP_ORIGIN', 'localhost')

    AUTH_WEB_TOKEN_CONFIRM_PATH = os.getenv('AUTH_WEB_TOKEN_CONFIRM_PATH')

    # JWT_OIDC Settings
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_ISSUER')

    TESTING = False
    DEBUG = False

    # Keycloak auth config baseurl
    KEYCLOAK_BASE_URL = os.getenv('KEYCLOAK_BASE_URL')
    KEYCLOAK_REALMNAME = os.getenv('KEYCLOAK_REALMNAME')
    KEYCLOAK_ADMIN_USERNAME = os.getenv('KEYCLOAK_ADMIN_CLIENTID')
    KEYCLOAK_ADMIN_SECRET = os.getenv('KEYCLOAK_ADMIN_SECRET')

    # Service account details
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('KEYCLOAK_SERVICE_ACCOUNT_ID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('KEYCLOAK_SERVICE_ACCOUNT_SECRET')

    # If any value is present in this flag, starts up a keycloak docker
    USE_TEST_KEYCLOAK_DOCKER = os.getenv('USE_TEST_KEYCLOAK_DOCKER', None)
    USE_DOCKER_MOCK = os.getenv('USE_DOCKER_MOCK', None)

    # Minio configuration values
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
    MINIO_ACCESS_SECRET = os.getenv('MINIO_ACCESS_SECRET')
    MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'account-mailer')
    MINIO_SECURE = True

    # PAD TOS PDF file name.
    PAD_TOS_FILE = os.getenv('PAD_TOS_FILE', 'BCROS-Business-Pre-Authorized-Debit-Agreement.pdf')


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """Creates the Development Config object."""

    TESTING = False
    DEBUG = True


class TestConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.

    Used by the py.test suite
    """

    DEBUG = True
    TESTING = True
    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_TEST_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_TEST_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_TEST_NAME', '')
    DB_HOST = os.getenv('DATABASE_TEST_HOST', '')
    DB_PORT = os.getenv('DATABASE_TEST_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_TEST_URL',
        default='postgresql://{user}:{password}@{host}:{port}/{name}'.format(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=int(DB_PORT), name=DB_NAME
        ),
    )

    STAN_CLUSTER_NAME = 'test-cluster'
    AUTH_WEB_TOKEN_CONFIRM_PATH = ''
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_TEST_ISSUER')
    # Service account details
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('KEYCLOAK_TEST_ADMIN_CLIENTID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('KEYCLOAK_TEST_ADMIN_SECRET')


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    TESTING = False
    DEBUG = False
