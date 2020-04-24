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
import os
import random
import time

import pytest
import sqlalchemy
from nats.aio.client import Client as Nats
from notify_api import applications
from notify_api.core import config as AppConfig
from notify_api.db.database import BASE, SESSION
from notify_api.db.models import NotificationStatusModel, NotificationTypeModel
from sqlalchemy import event
from stan.aio.client import Client as Stan
from starlette.testclient import TestClient

from notify_service import worker


DATABASE_URL = AppConfig.SQLALCHEMY_TEST_DATABASE_URI


@event.listens_for(NotificationTypeModel.__table__, 'after_create')
def insert_data(target, connection, **kw):  # pylint: disable=unused-argument
    """Load notification type data."""
    connection.execute(target.insert(),
                       {'code': 'EMAIL', 'desc': 'The Email type of notification', 'default': True},
                       {'code': 'TEXT', 'desc': 'The Text message type of notification', 'default': False})


@event.listens_for(NotificationStatusModel.__table__, 'after_create')
def insert_data2(target, connection, **kw):  # pylint: disable=unused-argument
    """Load notification status data."""
    connection.execute(target.insert(),
                       {'code': 'PENDING', 'desc': 'Initial state of the notification', 'default': True},
                       {'code': 'DELIVERED', 'desc': 'Status for the notification sent successful', 'default': False},
                       {'code': 'FAILURE', 'desc': 'Status for the notification sent failuree', 'default': False})


@pytest.fixture(scope='function', name='loop')
def loop_fixture():
    """Asyn event loop."""
    return asyncio.new_event_loop()


@pytest.fixture(scope='session', name='engine')
def engine_fixture():
    """Connect to the database."""
    engine = sqlalchemy.create_engine(AppConfig.SQLALCHEMY_TEST_DATABASE_URI)
    SESSION.configure(bind=engine)
    return engine


@pytest.fixture(scope='function', name='session')
def session_fixture(engine):
    """Create and drop all database metadata."""
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
    """FastAPI app."""
    return applications.NotifyAPI(
        engine,
        title='notify_api',
        version='0.0.0'
    )


@pytest.fixture(scope='function', name='client')
def client_fixture(app):
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture('function')
def client_id():
    """Return a unique client_id that can be used in tests."""
    _id = random.SystemRandom().getrandbits(0x58)
    return f'client-{_id}'


@pytest.fixture(scope='session')
def stan_server(docker_services):
    """Create the nats / stan services that the integration tests will use."""
    if os.getenv('TEST_NATS_DOCKER'):
        docker_services.start('nats')
        time.sleep(2)


@pytest.fixture(scope='function')
@pytest.mark.asyncio
async def notification_stan(event_loop, client_id):  # pylint: disable=redefined-outer-name
    """Create a stan connection for each function, to be used in the tests."""
    nats_client = Nats()
    stan_client = Stan()
    cluster_name = 'test-cluster'

    await nats_client.connect(io_loop=event_loop, name='entity.filing.tester')

    await stan_client.connect(cluster_name, client_id, nats=nats_client)

    yield stan_client

    await stan_client.close()
    await nats_client.close()


@pytest.fixture(scope='function')
def future(event_loop):
    """Return a future that is used for managing function tests."""
    _future = asyncio.Future(loop=event_loop)
    return _future


@pytest.fixture(scope='session')
def docker_compose_files(pytestconfig):
    """Get the docker-compose.yml absolute path."""
    return [
        os.path.join(str(pytestconfig.rootdir), 'tests/docker', 'docker-compose.yml')
    ]


@pytest.fixture()
def sendmail_mock(monkeypatch):
    """Mock send_with_send_message."""
    async def mock_send_message(*args, **kwargs):  # pylint: disable=unused-argument
        return True

    monkeypatch.setattr(worker, 'send_with_send_message', mock_send_message)


@pytest.fixture()
def sendmail_failed_mock(monkeypatch):
    """Mock send_with_send_message failed."""
    async def mock_send_message(*args, **kwargs):  # pylint: disable=unused-argument
        return False

    monkeypatch.setattr(worker, 'send_with_send_message', mock_send_message)
