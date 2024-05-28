# Copyright © 2024 Province of British Columbia
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
"""Common setup and fixtures for the pytest suite used by this service."""
from concurrent.futures import CancelledError
import logging
import os
import random
import time
from contextlib import contextmanager

import pytest
from auth_api import db as _db
from auth_api.services.rest_service import RestService
from flask_migrate import Migrate, upgrade
from sqlalchemy import event, text

from account_mailer import create_app


def setup_logging(conf):
    """Create the services logger.

    TODO should be reworked to load in the proper loggers and remove others
    """
    if conf and os.path.isfile(conf):
        logging.config.fileConfig(conf)


@contextmanager
def not_raises(exception):
    """Corallary to the pytest raises builtin.

    Assures that an exception is NOT thrown.
    """
    try:
        yield
    except exception:
        raise pytest.fail(f'DID RAISE {exception}')


@pytest.fixture(scope='session')
def app():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app('testing')

    # Bypass caching.
    def get_service_token():
        pass
    RestService.get_service_account_token = get_service_token

    return _app


@pytest.fixture(scope='session')
def db(app):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a session-wide initialised database.

    Drops all existing tables - Meta follows Postgres FKs
    """
    with app.app_context():
        drop_schema_sql = """DROP SCHEMA public CASCADE;
                                     CREATE SCHEMA public;
                                     GRANT ALL ON SCHEMA public TO postgres;
                                     GRANT ALL ON SCHEMA public TO public;
                                  """

        sess = _db.session()
        sess.execute(drop_schema_sql)
        sess.commit()

        # ############################################
        # There are 2 approaches, an empty database, or the same one that the app will use
        #     create the tables
        #     _db.create_all()
        # or
        # Use Alembic to load all of the DB revisions including supporting lookup data
        # This is the path we'll use in legal_api!!

        # even though this isn't referenced directly, it sets up the internal configs that upgrade
        import sys
        auth_api_folder = [folder for folder in sys.path if 'auth-api' in folder][0]
        migration_path = auth_api_folder.replace('/auth-api/src', '/auth-api/migrations')

        Migrate(app, _db, directory=migration_path)
        upgrade()

        # Restore the logging, alembic and sqlalchemy have their own logging from alembic.ini.
        setup_logging(os.path.abspath('logging.conf'))
        return _db


@pytest.fixture
def config(app):
    """Return the application config."""
    return app.config


@pytest.fixture(scope='session')
def client(app):  # pylint: disable=redefined-outer-name
    """Return a session-wide Flask test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def client_ctx(app):  # pylint: disable=redefined-outer-name
    """Return session-wide Flask test client."""
    with app.test_client() as _client:
        yield _client


@pytest.fixture(scope='function')
def client_id():
    """Return a unique client_id that can be used in tests."""
    _id = random.SystemRandom().getrandbits(0x58)
    #     _id = (base64.urlsafe_b64encode(uuid.uuid4().bytes)).replace('=', '')

    return f'client-{_id}'


@pytest.fixture(scope='function')
def session(app, db):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a function-scoped session."""
    with app.app_context():
        conn = db.engine.connect()
        txn = conn.begin()

        options = dict(bind=conn, binds={})
        sess = db.create_scoped_session(options=options)

        # establish  a SAVEPOINT just before beginning the test
        # (http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#using-savepoint)
        sess.begin_nested()

        @event.listens_for(sess(), 'after_transaction_end')
        def restart_savepoint(sess2, trans):  # pylint: disable=unused-variable
            # Detecting whether this is indeed the nested transaction of the test
            if trans.nested and not trans._parent.nested:  # pylint: disable=protected-access
                # Handle where test DOESN'T session.commit(),
                sess2.expire_all()
                sess.begin_nested()

        db.session = sess

        sql = text('select 1')
        sess.execute(sql)

        yield sess

        # Cleanup
        sess.remove()
        # This instruction rollsback any commit that were executed in the tests.
        txn.rollback()
        conn.close()


@pytest.fixture(scope='session', autouse=True)
def auto(docker_services, app):
    """Spin up a keycloak instance and initialize jwt."""
    if app.config['USE_TEST_KEYCLOAK_DOCKER']:
        docker_services.start('keycloak')
        docker_services.wait_for_service('keycloak', 8081)

    if app.config['USE_DOCKER_MOCK']:
        docker_services.start('notify')
        docker_services.start('minio')
        time.sleep(10)


@pytest.fixture(scope='session')
def docker_compose_files(pytestconfig):
    """Get the docker-compose.yml absolute path."""
    import os
    return [
        os.path.join(str(pytestconfig.rootdir), 'tests/docker', 'docker-compose.yml')
    ]


@pytest.fixture()
def auth_mock(monkeypatch):
    """Mock check_auth."""
    monkeypatch.setattr('auth_api.services.entity.check_auth', lambda *args, **kwargs: None)
    monkeypatch.setattr('auth_api.services.org.check_auth', lambda *args, **kwargs: None)
    monkeypatch.setattr('auth_api.services.invitation.check_auth', lambda *args, **kwargs: None)


@pytest.fixture()
def notify_mock(monkeypatch):
    """Mock send_email."""
    monkeypatch.setattr('auth_api.services.invitation.send_email', lambda *args, **kwargs: None)


@pytest.fixture()
def notify_org_mock(monkeypatch):
    """Mock send_email."""
    monkeypatch.setattr('auth_api.services.org.send_email', lambda *args, **kwargs: None)


@pytest.fixture()
def keycloak_mock(monkeypatch):
    """Mock keycloak services."""
    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService.join_account_holders_group',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService.remove_from_account_holders_group',
                        lambda *args, **kwargs: None)


@pytest.fixture(autouse=True)
def mock_queue_auth(mocker):
    """Mock queue authorization."""
    mocker.patch('auth_api.services.gcp_queue.gcp_auth.verify_jwt', return_value='')


@pytest.fixture(autouse=True)
def mock_pub_sub_call(mocker):
    """Mock pub sub call."""
    class PublisherMock:
        """Publisher Mock."""

        def __init__(self, *args, **kwargs):
            pass

        def publish(self, *args, **kwargs):
            """Publish mock."""
            raise CancelledError('This is a mock')

    mocker.patch('google.cloud.pubsub_v1.PublisherClient', PublisherMock)
