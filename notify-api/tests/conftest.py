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
"""Common setup and fixtures for the pytest suite used by this service."""
import asyncio

import pytest
import sqlalchemy
from sqlalchemy import event
from starlette.testclient import TestClient

from notify_api import applications
from notify_api.core import config as AppConfig
from notify_api.db.database import BASE, SESSION
from notify_api.db.models import NotificationStatusModel, NotificationTypeModel


DATABASE_URL = AppConfig.SQLALCHEMY_TEST_DATABASE_URI


@event.listens_for(NotificationTypeModel.__table__, 'after_create')
def insert_data(target, connection, **kw):
    connection.execute(target.insert(),
                       {'code': 'EMAIL', 'desc': 'The Email type of notification', 'default': True},
                       {'code': 'TEXT', 'desc': 'The Text message type of notification', 'default': False})


@event.listens_for(NotificationStatusModel.__table__, 'after_create')
def insert_data2(target, connection, **kw):
    connection.execute(target.insert(),
                       {'code': 'PENDING', 'desc': 'Initial state of the notification', 'default': True},
                       {'code': 'DELIVERED', 'desc': 'Status for the notification sent successful', 'default': False},
                       {'code': 'FAILURE', 'desc': 'Status for the notification sent failuree', 'default': False})


@pytest.fixture(scope='function', name='loop')
def loop_fixture():
    return asyncio.new_event_loop()


@pytest.fixture(scope='session', name='engine')
def engine_fixture():
    engine = sqlalchemy.create_engine(AppConfig.SQLALCHEMY_TEST_DATABASE_URI)
    SESSION.configure(bind=engine)
    return engine


@pytest.fixture(scope='function', name='session')
def session_fixture(engine):

    def _drop_all():
        meta = sqlalchemy.MetaData()
        meta.reflect(bind=engine)
        meta.drop_all(bind=engine)

    _drop_all()
    BASE.metadata.create_all(engine)

    session = SESSION()

    yield session
    session.close()

    _drop_all()


@pytest.fixture(scope='function', name='app')
def app_fixture(engine):
    return applications.NotifyAPI(
        engine,
        title='notify_api',
        version='0.0.0'
    )


@pytest.fixture(scope='function', name='client')
def client_fixture(app):
    return TestClient(app)
