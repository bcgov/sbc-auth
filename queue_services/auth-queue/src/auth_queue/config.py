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

from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

CONFIGURATION = {
    'development': 'names_events_listener.config.DevConfig',
    'testing': 'names_events_listener.config.TestConfig',
    'production': 'names_events_listener.config.ProdConfig',
    'default': 'names_events_listener.config.ProdConfig'
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


class _Config:  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SENTRY_ENABLE = os.getenv('SENTRY_ENABLE', 'False')
    SENTRY_DSN = os.getenv('SENTRY_DSN', None)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AUTH_LD_SDK_KEY = os.getenv('AUTH_LD_SDK_KEY', None)

    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_NAME', '')
    DB_HOST = os.getenv('DATABASE_HOST', '')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}'

    # PUB/SUB - PUB: account-mailer-dev, SUB: auth-event-dev and namex-nr-state-dev
    ACCOUNT_MAILER_TOPIC = os.getenv('ACCOUNT_MAILER_TOPIC', 'account-mailer-dev')
    # If blank in PUB/SUB, this should match the https endpoint the subscription is pushing to.
    AUTH_AUDIENCE_SUB = os.getenv('AUTH_QUEUE_AUDIENCE_SUB')
    GCP_AUTH_KEY = os.getenv('AUTHPAY_GCP_AUTH_KEY', None)
    VERIFY_PUBSUB_EMAILS = f'{os.getenv('AUTHPAY_SERVICE_ACCOUNT')},{os.getenv('BUSINESS_SERVICE_ACCOUNT')}'.split(',')

    PAY_API_URL = os.getenv('PAY_API_URL') + os.getenv('PAY_API_VERSION')

    # Service account details
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_ISSUER')
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('SBC_AUTH_ADMIN_CLIENT_ID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('SBC_AUTH_ADMIN_CLIENT_SECRET')


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
        default=f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}'
    )
    PAY_API_URL = os.getenv('PAY_API_URL') + os.getenv('PAY_API_VERSION')


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    TESTING = False
    DEBUG = False
