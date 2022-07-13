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
"""application config."""
import random

from starlette.config import Config


# Config will be read from environment variables and/or '.env' files.
CONFIG = Config('.env')

PROJECT_NAME = 'Notify Service'

TESTING = False
DEBUG = False

# POSTGRESQL
SQLALCHEMY_DATABASE_URI = CONFIG('NOTIFY_DATABASE_URL', cast=str)

# email server
MAIL_SERVER = CONFIG('MAIL_SERVER', cast=str, default='abcdabcd.smtp')
MAIL_PORT = CONFIG('MAIL_PORT', cast=int, default=25)
MAIL_USE_TLS = CONFIG('MAIL_USE_TLS', cast=str, default=False)
MAIL_USE_SSL = CONFIG('MAIL_USE_SSL', cast=str, default=False)
MAIL_USERNAME = CONFIG('MAIL_USERNAME', cast=str, default='')
MAIL_PASSWORD = CONFIG('MAIL_PASSWORD', cast=str, default='')
MAIL_FROM_ID = CONFIG('MAIL_FROM_ID', cast=str, default='abcabc@abcdabcd.com')

# Sentry Config
SENTRY_ENABLE = CONFIG('SENTRY_ENABLE', cast=str, default=False)
SENTRY_DSN = CONFIG('SENTRY_DSN', cast=str, default=None)

NATS_CLIENT_NAME = CONFIG('NATS_CLIENT_NAME', cast=str, default='notifiations.worker')
NATS_CLUSTER_ID = CONFIG('NATS_CLUSTER_ID', cast=str, default='test-cluster')
NATS_QUEUE = CONFIG('NATS_QUEUE', cast=str, default='notifiations-worker')
NATS_SERVERS = CONFIG('NATS_SERVERS', cast=str, default='nats://127.0.0.1:4222')
NATS_SUBJECT = CONFIG('NATS_SUBJECT', cast=str, default='notifiations')
NATS_FILER_SUBJECT = CONFIG('NATS_FILER_SUBJECT', cast=str, default='notifications.filer')

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
    'subject': CONFIG('NATS_FILER_SUBJECT', cast=str, default='notifications.filer'),
}

DELIVERY_FAILURE_RETRY_TIME_FRAME = CONFIG('DELIVERY_FAILURE_RETRY_TIME_FRAME', cast=int, default=7200)
PENDING_EMAIL_TIME_FRAME = CONFIG('PENDING_EMAIL_TIME_FRAME', cast=int, default=300)
FAILURE_EMAIL_TIME_FRAME = CONFIG('FAILURE_EMAIL_TIME_FRAME', cast=int, default=600)

SQLALCHEMY_TEST_DATABASE_URI = CONFIG('NOTIFY_DATABASE_TEST_URL', cast=str)
