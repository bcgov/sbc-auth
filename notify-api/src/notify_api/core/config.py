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
from starlette.datastructures import Secret


# Config will be read from environment variables and/or '.env' files.
CONFIG = Config('.env')

PROJECT_NAME = 'Notify API'

API_V1_STR = '/api/v1'

TESTING = False
DEBUG = False
# SECRET_KEY = CONFIG('SECRET_KEY', cast=Secret)
# ALLOWED_HOSTS = CONFIG('ALLOWED_HOSTS', cast=CommaSeparatedStrings, default='[*]')


# POSTGRESQL
DATABASE_USER = CONFIG('DATABASE_USERNAME', cast=str, default='')
DATABASE_PASSWORD = CONFIG('DATABASE_PASSWORD', cast=Secret, default='')
DATABASE_NAME = CONFIG('DATABASE_NAME', cast=str, default='')
DATABASE_HOST = CONFIG('DATABASE_HOST', cast=str, default='')
DATABASE_PORT = CONFIG('DATABASE_PORT', cast=int, default=5432)
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=int(DATABASE_PORT),
    name=DATABASE_NAME,
)


# email server
MAIL_SERVER = CONFIG('MAIL_SERVER', cast=str, default='abcdabcd..smtp')
MAIL_PORT = CONFIG('MAIL_PORT', cast=int, default=25)
MAIL_USE_TLS = CONFIG('MAIL_USE_TLS', cast=str, default=False)
MAIL_USE_SSL = CONFIG('MAIL_USE_SSL', cast=str, default=False)
MAIL_USERNAME = CONFIG('MAIL_USERNAME', cast=str, default='')
MAIL_PASSWORD = CONFIG('MAIL_PASSWORD', cast=str, default='')
MAIL_FROM_ID = CONFIG('MAIL_FROM_ID', cast=str, default='abcabc@abcdabcd.com')


# Sentry Config
SENTRY_DSN = CONFIG('SENTRY_DSN', cast=str, default=None)

NATS_CLIENT_NAME = CONFIG('NATS_CLIENT_NAME', cast=str, default='entity.notifiation.worker')
NATS_CLUSTER_ID = CONFIG('NATS_CLUSTER_ID', cast=str, default='test-cluster')
NATS_QUEUE = CONFIG('NATS_QUEUE', cast=str, default='notifiation-worker')
NATS_SERVERS = CONFIG('NATS_SERVERS', cast=str, default='nats://127.0.0.1:4222')
NATS_SUBJECT = CONFIG('NATS_SUBJECT', cast=str, default='entity.notifiations')

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

DELIVERY_FAILURE_RETRY_TIME_FRAME = CONFIG('DELIVERY_FAILURE_RETRY_TIME_FRAME', cast=int, default=2)
PENDING_EMAIL_TIME_FRAME = CONFIG('PENDING_EMAIL_TIME_FRAME', cast=int, default=300)
FAILURE_EMAIL_TIME_FRAME = CONFIG('FAILURE_EMAIL_TIME_FRAME', cast=int, default=600)

DB_USER = CONFIG('DATABASE_TEST_USERNAME', cast=str, default='postgres')
DB_PASSWORD = CONFIG('DATABASE_TEST_PASSWORD', cast=Secret, default='postgres')
DB_NAME = CONFIG('DATABASE_TEST_NAME', cast=str, default='postgres')
DB_HOST = CONFIG('DATABASE_TEST_HOST', cast=str, default='localhost')
DB_PORT = CONFIG('DATABASE_TEST_PORT', cast=int, default=5432)
SQLALCHEMY_TEST_DATABASE_URI = CONFIG(
    'DATABASE_TEST_URL',
    default='postgresql://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=int(DB_PORT), name=DB_NAME
    ),
)
