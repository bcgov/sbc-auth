# Copyright © 2019 Province of British Columbia
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
"""All of the configuration for the service is captured here.

All items are loaded,
or have Constants defined here that are loaded into the Flask configuration.
All modules and lookups get their configuration from the Flask config,
rather than reading environment variables directly or by accessing this configuration directly.
"""

import logging
import os
import sys
from typing import List

from dotenv import find_dotenv, load_dotenv

# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

CONFIGURATION = {
    'development': 'auth_api.config.DevConfig',
    'testing': 'auth_api.config.TestConfig',
    'production': 'auth_api.config.ProdConfig',
    'default': 'auth_api.config.ProdConfig'
}


def get_named_config(config_name: str = 'production'):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ['production', 'staging', 'default']:
        config = ProdConfig()
    elif config_name == 'testing':
        config = TestConfig()
    elif config_name == 'development':
        config = DevConfig()
    else:
        raise KeyError("Unknown configuration '{config_name}'")
    return config


class _Config:  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults for all the other configurations."""

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = 'a secret'
    AUTH_LD_SDK_KEY = os.getenv('AUTH_LD_SDK_KEY', None)

    TESTING = False
    DEBUG = False

    ALEMBIC_INI = 'migrations/alembic.ini'
    # Config to skip migrations when alembic migrate is used
    SKIPPED_MIGRATIONS = ['authorizations_view']

    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_NAME', '')
    DB_HOST = os.getenv('DATABASE_HOST', '')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT_OIDC Settings
    JWT_OIDC_WELL_KNOWN_CONFIG = os.getenv('JWT_OIDC_WELL_KNOWN_CONFIG')
    JWT_OIDC_ALGORITHMS = os.getenv('JWT_OIDC_ALGORITHMS')
    JWT_OIDC_JWKS_URI = os.getenv('JWT_OIDC_JWKS_URI')
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_ISSUER')
    JWT_OIDC_AUDIENCE = os.getenv('JWT_OIDC_AUDIENCE')
    JWT_OIDC_CLIENT_SECRET = os.getenv('JWT_OIDC_CLIENT_SECRET')
    JWT_OIDC_CACHING_ENABLED = os.getenv('JWT_OIDC_CACHING_ENABLED')
    try:
        JWT_OIDC_JWKS_CACHE_TIMEOUT = int(os.getenv('JWT_OIDC_JWKS_CACHE_TIMEOUT'))
    except:  # pylint:disable=bare-except # noqa: B901, E722
        JWT_OIDC_JWKS_CACHE_TIMEOUT = 300

    # Keycloak auth config baseurl
    KEYCLOAK_BASE_URL = os.getenv('KEYCLOAK_BASE_URL')
    KEYCLOAK_REALMNAME = os.getenv('KEYCLOAK_REALMNAME')
    KEYCLOAK_ADMIN_USERNAME = os.getenv('SBC_AUTH_ADMIN_CLIENT_ID')
    KEYCLOAK_ADMIN_SECRET = os.getenv('SBC_AUTH_ADMIN_CLIENT_SECRET')

    # keycloak service account token lifepan
    try:
        CACHE_DEFAULT_TIMEOUT = int(os.getenv('ACCESS_TOKEN_LIFESPAN'))
    except:  # pylint:disable=bare-except # noqa: B901, E722
        CACHE_DEFAULT_TIMEOUT = 300

    CACHE_MEMCACHED_SERVERS = os.getenv('CACHE_MEMCACHED_SERVERS')

    CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST')
    CACHE_REDIS_PORT = os.getenv('CACHE_REDIS_PORT')

    # Service account details
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('SBC_AUTH_ADMIN_CLIENT_ID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('SBC_AUTH_ADMIN_CLIENT_SECRET')

    ENTITY_SVC_CLIENT_ID = os.getenv('ENTITY_SERVICE_ACCOUNT_CLIENT_ID')
    ENTITY_SVC_CLIENT_SECRET = os.getenv('ENTITY_SERVICE_ACCOUNT_CLIENT_SECRET')

    # Upstream Keycloak settings
    KEYCLOAK_BCROS_BASE_URL = os.getenv('KEYCLOAK_BCROS_BASE_URL')
    KEYCLOAK_BCROS_REALMNAME = os.getenv('KEYCLOAK_BCROS_REALMNAME')
    KEYCLOAK_BCROS_ADMIN_CLIENTID = os.getenv('KEYCLOAK_BCROS_ADMIN_CLIENTID')
    KEYCLOAK_BCROS_ADMIN_SECRET = os.getenv('KEYCLOAK_BCROS_ADMIN_SECRET')

    # API Endpoints
    BCOL_API_URL = os.getenv('BCOL_API_URL')
    LEGAL_API_URL = os.getenv('LEGAL_API_URL', '')
    NAMEX_API_URL = os.getenv('NAMEX_API_URL', '')
    NOTIFY_API_URL = os.getenv('NOTIFY_API_URL')
    PAY_API_SANDBOX_URL = os.getenv('PAY_API_SANDBOX_URL')
    PAY_API_URL = os.getenv('PAY_API_URL')

    LEGAL_API_VERSION = os.getenv('LEGAL_API_VERSION')
    LEGAL_API_VERSION_2 = os.getenv('LEGAL_API_VERSION_2', '')

    LEAR_AFFILIATION_DETAILS_URL = f'{LEGAL_API_URL + LEGAL_API_VERSION_2}/businesses/search'
    NAMEX_AFFILIATION_DETAILS_URL = f'{NAMEX_API_URL}/requests/search'

    # PUB/SUB - PUB: account-mailer-dev, auth-event-dev
    GCP_AUTH_KEY = os.getenv('GCP_AUTH_KEY', None)
    ACCOUNT_MAILER_TOPIC = os.getenv('ACCOUNT_MAILER_TOPIC', 'account-mailer-dev')
    AUTH_EVENT_TOPIC = os.getenv('AUTH_EVENT_TOPIC', 'auth-event-dev')

    # Minio configuration values
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
    MINIO_ACCESS_SECRET = os.getenv('MINIO_ACCESS_SECRET')
    MINIO_BUCKET_ACCOUNTS = os.getenv('MINIO_BUCKET_ACCOUNTS', 'accounts')
    MINIO_SECURE = True

    # email
    MAIL_FROM_ID = os.getenv('MAIL_FROM_ID')

    # mail token  configuration
    AUTH_WEB_TOKEN_CONFIRM_PATH = os.getenv('AUTH_WEB_TOKEN_CONFIRM_PATH')
    EMAIL_SECURITY_PASSWORD_SALT = os.getenv('EMAIL_SECURITY_PASSWORD_SALT')
    EMAIL_TOKEN_SECRET_KEY = os.getenv('EMAIL_TOKEN_SECRET_KEY')
    TOKEN_EXPIRY_PERIOD = os.getenv('TOKEN_EXPIRY_PERIOD')
    AFFILIATION_TOKEN_EXPIRY_PERIOD_MINS = os.getenv('AFFILIATION_TOKEN_EXPIRY_PERIOD_MINS', '15')
    STAFF_ADMIN_EMAIL = os.getenv('STAFF_ADMIN_EMAIL')

    # Sentry Config
    SENTRY_ENABLE = os.getenv('SENTRY_ENABLE', 'False')
    SENTRY_DSN = os.getenv('SENTRY_DSN', None)

    # front end serves this image in this name.can be moved to openshift config as well..
    REGISTRIES_LOGO_IMAGE_NAME = 'bc_logo_for_email.png'

    # url for the front end app
    WEB_APP_URL = os.getenv('WEB_APP_URL')

    # url for the front end app
    BCEID_SIGNIN_ROUTE = os.getenv('BCEID_SIGNIN_ROUTE', 'signin/bceid')
    # url for the front end app
    BCEID_ACCOUNT_SETUP_ROUTE = os.getenv('BCEID_ACCOUNT_SETUP_ROUTE', 'setup-non-bcsc-account')
    BCEID_ADMIN_SETUP_ROUTE = os.getenv('BCEID_ADMIN_SETUP_ROUTE', 're-upload-affidavit')

    try:
        MAX_NUMBER_OF_ORGS = int(os.getenv('MAX_NUMBER_OF_ORGS'))
    except:  # pylint:disable=bare-except # noqa: B901, E722
        MAX_NUMBER_OF_ORGS = 3

    BCOL_ACCOUNT_LINK_CHECK = os.getenv('BCOL_ACCOUNT_LINK_CHECK', 'True').lower() == 'true'

    # Till direct pay is fully ready , keep this value false
    DIRECT_PAY_ENABLED = os.getenv('DIRECT_PAY_ENABLED', 'False').lower() == 'true'

    # Config value to disable activity logs
    DISABLE_ACTIVITY_LOGS = os.getenv('DISABLE_ACTIVITY_LOGS', 'False').lower() == 'true'

    # API gateway config
    API_GW_CONSUMERS_API_URL = os.getenv('API_GW_CONSUMERS_API_URL', None)
    API_GW_KEY = os.getenv('API_GW_KEY', None)
    API_GW_CONSUMERS_SANDBOX_API_URL = os.getenv('API_GW_CONSUMERS_SANDBOX_API_URL', None)
    API_GW_NON_PROD_KEY = os.getenv('API_GW_NON_PROD_KEY', None)
    API_GW_EMAIL_SUFFIX = os.getenv('API_GW_EMAIL_SUFFIX', None)
    API_GW_KC_CLIENT_ID_PATTERN = os.getenv('API_GW_KC_CLIENT_ID_PATTERN', 'api-key-account-{account_id}')

    # NR Supported Request types.
    NR_SUPPORTED_REQUEST_TYPES: List[str] = os.getenv('NR_SUPPORTED_REQUEST_TYPES', 'BC').replace(' ', '').split(',')
    AUTH_WEB_SANDBOX_HOST = os.getenv('AUTH_WEB_SANDBOX_HOST', 'localhost')


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """Dev Config."""

    TESTING = False
    DEBUG = True
    if os.getenv('DISABLE_JAEGER_TRACING', 'False').lower() == 'true':
        logging.getLogger('jaeger_tracing').disabled = True


class TestConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.used by the py.test suite."""

    DEBUG = True
    TESTING = True
    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_TEST_USERNAME', 'postgres')
    DB_PASSWORD = os.getenv('DATABASE_TEST_PASSWORD', 'postgres')
    DB_NAME = os.getenv('DATABASE_TEST_NAME', 'postgres')
    DB_HOST = os.getenv('DATABASE_TEST_HOST', 'localhost')
    DB_PORT = os.getenv('DATABASE_TEST_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL',
                                        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}')

    # JWT OIDC settings
    # JWT_OIDC_TEST_MODE will set jwt_manager to use
    JWT_OIDC_TEST_MODE = True
    JWT_OIDC_TEST_AUDIENCE = os.getenv('JWT_OIDC_TEST_AUDIENCE')
    JWT_OIDC_TEST_CLIENT_SECRET = os.getenv('JWT_OIDC_TEST_CLIENT_SECRET')
    JWT_OIDC_TEST_ISSUER = os.getenv('JWT_OIDC_TEST_ISSUER')
    JWT_OIDC_TEST_ALGORITHMS = os.getenv('JWT_OIDC_TEST_ALGORITHMS')
    JWT_OIDC_TEST_KEYS = {
        'keys': [
            {
                'kid': 'sbc-auth-web',
                'kty': 'RSA',
                'alg': 'RS256',
                'use': 'sig',
                'n': 'AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-'
                     'TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR',
                'e': 'AQAB'
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_JWKS = {
        'keys': [
            {
                'kid': 'sbc-auth-web',
                'kty': 'RSA',
                'alg': 'RS256',
                'use': 'sig',
                'n': 'AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-'
                     'TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR',
                'e': 'AQAB',
                'd': 'C0G3QGI6OQ6tvbCNYGCqq043YI_8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhskURaDwk4-'
                     '8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh_'
                     'xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0',
                'p': 'APXcusFMQNHjh6KVD_hOUIw87lvK13WkDEeeuqAydai9Ig9JKEAAfV94W6Aftka7tGgE7ulg1vo3eJoLWJ1zvKM',
                'q': 'AOjX3OnPJnk0ZFUQBwhduCweRi37I6DAdLTnhDvcPTrrNWuKPg9uGwHjzFCJgKd8KBaDQ0X1rZTZLTqi3peT43s',
                'dp': 'AN9kBoA5o6_Rl9zeqdsIdWFmv4DB5lEqlEnC7HlAP-3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhc',
                'dq': 'ANtbSY6njfpPploQsF9sU26U0s7MsuLljM1E8uml8bVJE1mNsiu9MgpUvg39jEu9BtM2tDD7Y51AAIEmIQex1nM',
                'qi': 'XLE5O360x-MhsdFXx8Vwz4304-MJg-oGSJXCK_ZWYOB_FGXFRTfebxCsSYi0YwJo-oNu96bvZCuMplzRI1liZw'
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_PEM = """
    -----BEGIN RSA PRIVATE KEY-----
    MIICXQIBAAKBgQDfn1nKQshOSj8xw44oC2klFWSNLmK3BnHONCJ1bZfq0EQ5gIfg
    tlvB+Px8Ya+VS3OnK7Cdi4iU1fxO9ktN6c6TjmmmFevk8wIwqLthmCSF3r+3+h4e
    ddj7hucMsXWv05QUrCPoL6YUUz7Cgpz7ra24rpAmK5z7lsV+f3BEvXkrUQIDAQAB
    AoGAC0G3QGI6OQ6tvbCNYGCqq043YI/8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhs
    kURaDwk4+8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh/
    xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0CQQD13LrBTEDR44ei
    lQ/4TlCMPO5bytd1pAxHnrqgMnWovSIPSShAAH1feFugH7ZGu7RoBO7pYNb6N3ia
    C1idc7yjAkEA6Nfc6c8meTRkVRAHCF24LB5GLfsjoMB0tOeEO9w9Ous1a4o+D24b
    AePMUImAp3woFoNDRfWtlNktOqLel5PjewJBAN9kBoA5o6/Rl9zeqdsIdWFmv4DB
    5lEqlEnC7HlAP+3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhcCQQDb
    W0mOp436T6ZaELBfbFNulNLOzLLi5YzNRPLppfG1SRNZjbIrvTIKVL4N/YxLvQbT
    NrQw+2OdQACBJiEHsdZzAkBcsTk7frTH4yGx0VfHxXDPjfTj4wmD6gZIlcIr9lZg
    4H8UZcVFN95vEKxJiLRjAmj6g273pu9kK4ymXNEjWWJn
    -----END RSA PRIVATE KEY-----"""

    KEYCLOAK_ADMIN_USERNAME = KEYCLOAK_BCROS_ADMIN_CLIENTID = os.getenv('KEYCLOAK_TEST_ADMIN_CLIENTID')
    KEYCLOAK_ADMIN_SECRET = KEYCLOAK_BCROS_ADMIN_SECRET = os.getenv('KEYCLOAK_TEST_ADMIN_SECRET')
    KEYCLOAK_BASE_URL = KEYCLOAK_BCROS_BASE_URL = os.getenv('KEYCLOAK_TEST_BASE_URL')
    KEYCLOAK_REALMNAME = KEYCLOAK_BCROS_REALMNAME = os.getenv('KEYCLOAK_TEST_REALMNAME')
    JWT_OIDC_AUDIENCE = os.getenv('JWT_OIDC_TEST_AUDIENCE')
    JWT_OIDC_CLIENT_SECRET = os.getenv('JWT_OIDC_TEST_CLIENT_SECRET')
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_TEST_ISSUER')
    # Service account details
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv('KEYCLOAK_TEST_ADMIN_CLIENTID')
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv('KEYCLOAK_TEST_ADMIN_SECRET')

    # Legal-API URL
    ENTITY_SVC_CLIENT_ID = os.getenv('KEYCLOAK_TEST_ADMIN_CLIENTID')
    ENTITY_SVC_CLIENT_SECRET = os.getenv('KEYCLOAK_TEST_ADMIN_SECRET')

    LEGAL_API_URL = 'https://mock-auth-tools.pathfinder.gov.bc.ca/rest/legal-api/2.7'
    LEGAL_API_VERSION_2 = '/api/v1'

    NOTIFY_API_URL = 'http://localhost:8080/notify-api/api/v1'
    BCOL_API_URL = 'http://localhost:8080/bcol-api/api/v1'
    PAY_API_URL = 'http://localhost:8080/pay-api/api/v1'
    PAY_API_SANDBOX_URL = 'http://localhost:8080/pay-api/api/v1'

    # If any value is present in this flag, starts up a keycloak docker
    USE_TEST_KEYCLOAK_DOCKER = os.getenv('USE_TEST_KEYCLOAK_DOCKER', None)
    USE_DOCKER_MOCK = os.getenv('USE_DOCKER_MOCK', None)
    MAX_NUMBER_OF_ORGS = 3

    BCOL_ACCOUNT_LINK_CHECK = True

    # Minio variables
    MINIO_ENDPOINT = 'localhost:9000'
    MINIO_ACCESS_KEY = 'minio'
    MINIO_ACCESS_SECRET = 'minio123'
    MINIO_BUCKET_ACCOUNTS = 'accounts'
    MINIO_SECURE = False

    STAFF_ADMIN_EMAIL = 'test@test.com'
    ACCOUNT_MAILER_TOPIC = os.getenv('ACCOUNT_MAILER_TOPIC', 'account-mailer-dev')

    API_GW_CONSUMERS_API_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget'
    API_GW_CONSUMERS_SANDBOX_API_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget'
    API_GW_CONSUMER_EMAIL = 'test.all.mc@gov.bc.ca'


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    SECRET_KEY = os.getenv('SECRET_KEY', None)

    if not SECRET_KEY:
        SECRET_KEY = os.urandom(24)
        print('WARNING: SECRET_KEY being set as a one-shot', file=sys.stderr)

    TESTING = False
    DEBUG = False
