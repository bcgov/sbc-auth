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

    TESTING = False
    DEBUG = False

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
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    # Keycloak & Jwt
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_ISSUER')

    # Keycloak auth config baseurl
    KEYCLOAK_BASE_URL = os.getenv('KEYCLOAK_BASE_URL')
    KEYCLOAK_REALMNAME = os.getenv('KEYCLOAK_REALMNAME')
    KEYCLOAK_ADMIN_USERNAME = os.getenv('SBC_AUTH_ADMIN_CLIENT_ID')
    KEYCLOAK_ADMIN_SECRET = os.getenv('SBC_AUTH_ADMIN_CLIENT_SECRET')

    # Service account details
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('SBC_AUTH_ADMIN_CLIENT_ID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('SBC_AUTH_ADMIN_CLIENT_SECRET')

    # API endpoints
    PAY_API_URL = os.getenv('PAY_API_URL')
    NOTIFY_API_URL = os.getenv('NOTIFY_API_URL')
    REPORT_API_BASE_URL = f'{os.getenv("REPORT_API_URL")}/reports'

    # PUB/SUB
    ACCOUNT_MAILER_TOPIC = os.getenv('ACCOUNT_MAILER_TOPIC', 'account-mailer-dev')
    AUTH_SUB_AUDIENCE = os.getenv('AUTH_SUB_AUDIENCE')

    # Minio configuration values
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
    MINIO_ACCESS_SECRET = os.getenv('MINIO_ACCESS_SECRET')
    MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'account-mailer')
    MINIO_SECURE = os.getenv('MINIO_SECURE', 'true').lower() == 'true'

    REFUND_REQUEST = {
        'creditcard': {
            'recipients': os.getenv('REFUND_REQUEST_RECIPIENTS', '')
        },
        'bcol': {
            'recipients': os.getenv('BCOL_REFUND_REQUEST_RECIPIENTS', '')
        }
    }

    # application setting
    PDF_TEMPLATE_PATH = os.getenv('PDF_TEMPLATE_PATH', 'src/account_mailer/pdf_templates')
    TEMPLATE_PATH = os.getenv('TEMPLATE_PATH', 'src/account_mailer/email_templates')
    HTTP_ORIGIN = os.getenv('HTTP_ORIGIN', 'localhost')
    WEB_APP_URL = os.getenv('WEB_APP_URL', 'localhost')
    WEB_APP_STATEMENT_PATH_URL = os.getenv('WEB_APP_STATEMENT_PATH_URL', 'account/orgId/settings/statements')
    DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'localhost')
    AUTH_WEB_TOKEN_CONFIRM_PATH = os.getenv('AUTH_WEB_TOKEN_CONFIRM_PATH')
    # PAD TOS PDF file name.
    PAD_TOS_FILE = os.getenv('PAD_TOS_FILE', 'BCROS-Business-Pre-Authorized-Debit-Agreement.pdf')
    # MHR QUALIFIED SUPPLIER PDF File name
    MHR_QS_AGREEMENT_FILE = os.getenv('MHR_QS_AGREEMENT_FILE', 'MHR_QualifiedSuppliersAgreement.pdf')

    # If any value is present in this flag, starts up a keycloak docker
    USE_TEST_KEYCLOAK_DOCKER = os.getenv('USE_TEST_KEYCLOAK_DOCKER', None)
    USE_DOCKER_MOCK = os.getenv('USE_DOCKER_MOCK', None)

    # BC online admin email
    BCOL_ADMIN_EMAIL = os.getenv('BCOL_ADMIN_EMAIL', 'test@test.com')

    LEGISLATIVE_TIMEZONE = os.getenv('LEGISLATIVE_TIMEZONE', 'America/Vancouver')


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
        default=f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    )

    AUTH_WEB_TOKEN_CONFIRM_PATH = ''
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_TEST_ISSUER')
    # Service account details
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('KEYCLOAK_TEST_ADMIN_CLIENTID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('KEYCLOAK_TEST_ADMIN_SECRET')
    BCOL_ADMIN_EMAIL = 'test@test.com'

    # Minio variables
    MINIO_ENDPOINT = 'localhost:9000'
    MINIO_ACCESS_KEY = 'minio'
    MINIO_ACCESS_SECRET = 'minio123'
    MINIO_BUCKET_NAME = 'cgi-ejv'
    MINIO_SECURE = False


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    TESTING = False
    DEBUG = False
