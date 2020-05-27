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
"""application config."""
import random

from functools import lru_cache
from pydantic import BaseSettings


class APISettings(BaseSettings):
    """API settings."""

    PROJECT_NAME = 'Notify API'

    API_V1_STR = '/api/v1'

    # POSTGRESQL
    DATABASE_URL: str = ''
    DATABASE_TEST_URL: str = ''

    # email server
    MAIL_SERVE: str = ''
    MAIL_PORT: int = 25
    MAIL_USE_TLS: str = None
    MAIL_USE_SSL: str = None
    MAIL_USERNAME: str = ''
    MAIL_PASSWORD: str = ''
    MAIL_FROM_ID: str = ''

    # Sentry Config
    SENTRY_DSN: str = None

    NATS_CLIENT_NAME: str = 'notifiations.worker'
    NATS_CLUSTER_ID: str = 'test-cluster'
    NATS_QUEUE: str = 'notifiations-worker'
    NATS_SERVERS: str = 'nats://127.0.0.1:4222'
    NATS_SUBJECT: str = 'notifiations'
    NATS_FILER_SUBJECT: str = 'notifications.filer'

    NATS_CONNECTION_OPTIONS = {
        'servers': NATS_SERVERS.split(','),
        'name': NATS_CLIENT_NAME

    }
    STAN_CONNECTION_OPTIONS = {
        'cluster_id': NATS_CLUSTER_ID,
        'client_id': str(random.SystemRandom().getrandbits(0x58)),
        'ping_interval': 1,
        'ping_max_out': 5,
    }

    SUBSCRIPTION_OPTIONS = {
        'subject': NATS_SUBJECT,
        'queue': NATS_QUEUE,
        'durable_name': NATS_QUEUE + '_durable',
    }

    FILER_PUBLISH_OPTIONS = {
        'subject': NATS_FILER_SUBJECT,
    }

    DELIVERY_FAILURE_RETRY_TIME_FRAME: int = 7200
    PENDING_EMAIL_TIME_FRAME: int = 300
    FAILURE_EMAIL_TIME_FRAME: int = 600

    # JWT_OIDC Settings
    JWT_OIDC_WELL_KNOWN_CONFIG: str = None
    JWT_OIDC_ALGORITHMS: str = 'RS256'
    JWT_OIDC_JWKS_URI: str = None
    JWT_OIDC_ISSUER: str = None
    JWT_OIDC_AUDIENCE: str = None
    JWT_OIDC_CLIENT_SECRET: str = None
    JWT_OIDC_CACHING_ENABLED: bool = False
    JWT_OIDC_JWKS_CACHE_TIMEOUT: int = 300

    class Config:  # pylint: disable=too-few-public-methods
        """Config."""

        env_file = '.env'
        case_sensitive = True


@lru_cache()
def get_api_settings() -> APISettings:
    """Get settings."""
    return APISettings()  # reads variables from environment
