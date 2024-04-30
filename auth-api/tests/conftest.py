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
"""Common setup and fixtures for the pytest suite used by this service."""
import os
import time
from random import random

import pytest
from flask_migrate import Migrate, upgrade
from sqlalchemy import event, text

from auth_api import create_app, setup_jwt_manager
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException, Error
from auth_api.models import db as _db


def mock_token(config_id='', config_secret=''):
    """Mock token generator."""
    return 'TOKEN....'


@pytest.fixture(scope='session')
def app():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app('testing')

    return _app


@pytest.fixture(scope='function')
def app_request():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app('testing')

    return _app


@pytest.fixture(scope='session')
def client(app):  # pylint: disable=redefined-outer-name
    """Return a session-wide Flask test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def jwt():
    """Return a session-wide jwt manager."""
    return _jwt


@pytest.fixture(scope='session')
def client_ctx(app):  # pylint: disable=redefined-outer-name
    """Return session-wide Flask test client."""
    with app.test_client() as _client:
        yield _client


@pytest.fixture(scope='session')
def db(app):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a session-wide initialised database.

    Drops schema, and recreate.
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
        # This is the path we'll use in auth_api!!

        # even though this isn't referenced directly, it sets up the internal configs that upgrade needs
        Migrate(app, _db)
        upgrade()

        return _db


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


@pytest.fixture(scope='function')
def client_id():
    """Return a unique client_id that can be used in tests."""
    _id = random.SystemRandom().getrandbits(0x58)
    #     _id = (base64.urlsafe_b64encode(uuid.uuid4().bytes)).replace('=', '')

    return f'client-{_id}'


@pytest.fixture(scope='session')
def stan_server(docker_services):
    """Create the nats / stan services that the integration tests will use."""
    if os.getenv('USE_DOCKER_MOCK'):
        docker_services.start('nats')
        time.sleep(2)


@pytest.fixture(scope='session', autouse=True)
def auto(docker_services, app):
    """Spin up a keycloak instance and initialize jwt."""
    if app.config['USE_TEST_KEYCLOAK_DOCKER']:
        docker_services.start('keycloak')
        docker_services.wait_for_service('keycloak', 8081)

    setup_jwt_manager(app, _jwt)

    if app.config['USE_DOCKER_MOCK']:
        docker_services.start('minio')
        docker_services.start('notify')
        docker_services.start('bcol')
        docker_services.start('pay')
        docker_services.start('proxy')
        docker_services.wait_for_service('minio', 9000)
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
    monkeypatch.setattr('auth_api.services.affiliation_invitation.check_auth', lambda *args, **kwargs: None)


@pytest.fixture()
def notify_mock(monkeypatch):
    """Mock send_email."""
    monkeypatch.setattr('auth_api.services.invitation.send_email', lambda *args, **kwargs: None)
    monkeypatch.setattr('auth_api.services.affiliation_invitation.send_email', lambda *args, **kwargs: None)


@pytest.fixture()
def notify_org_mock(monkeypatch):
    """Mock send_email."""
    monkeypatch.setattr('auth_api.services.org.send_email', lambda *args, **kwargs: None)


@pytest.fixture()
def keycloak_mock(monkeypatch):
    """Mock keycloak services."""
    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService.join_account_holders_group',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService.join_users_group',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService.remove_from_account_holders_group',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr('auth_api.services.keycloak.KeycloakService.add_or_remove_product_keycloak_groups',
                        lambda *args, **kwargs: None)


@pytest.fixture()
def business_exception_mock(monkeypatch):
    """Mock get business call exceotion."""

    def get_business(business_identifier, token):
        raise BusinessException(Error.AFFILIATION_INVITATION_BUSINESS_NOT_FOUND, None)

    monkeypatch.setattr('auth_api.services.affiliation_invitation.AffiliationInvitation._get_business_details',
                        get_business)


@pytest.fixture()
def business_mock(monkeypatch):
    """Mock get business call."""

    def get_business(business_identifier, token):
        return {
            'business': {
                'identifier': 'CP0002103',
                'legalName': 'BarFoo, Inc.',
                'legalType': 'CP'
            }
        }

    def get_businesses(business_identifiers, token):
        return [
            {
                'identifier': 'CP0002103',
                'legalName': 'BarFoo, Inc.',
                'legalType': 'CP',
                'state': 'ACTIVE',
            },
            {

                'identifier': 'CP0002104',
                'legalName': 'BarFooMeToo, Inc.',
                'legalType': 'CP',
                'state': 'ACTIVE',
            }
        ]

    monkeypatch.setattr('auth_api.services.affiliation_invitation.AffiliationInvitation._get_business_details',
                        get_business)

    monkeypatch.setattr('auth_api.services.affiliation_invitation.AffiliationInvitation._get_multiple_business_details',
                        get_businesses)


@pytest.fixture()
def nr_mock(monkeypatch):
    """Mock nr get call."""

    def get_nr(business_identifier):
        return {
            'applicants': {
                'emailAddress': 'test@test.com',
                'phoneNumber': '1112223333'
            },
            'names': [
                {
                    'name': 'TEST INC..',
                    'state': 'APPROVED'
                }
            ],
            'state': 'APPROVED',
            'requestTypeCd': 'BC'
        }

    monkeypatch.setattr('auth_api.services.affiliation.Affiliation._get_nr_details', get_nr)


@pytest.fixture()
def minio_mock(monkeypatch):
    """Mock minio calls."""

    def get_nr(business_identifier):
        return {
            'applicants': {
                'emailAddress': 'test@test.com',
                'phoneNumber': '1112223333'
            },
            'names': [
                {
                    'name': 'TEST INC..',
                    'state': 'APPROVED'
                }
            ],
            'state': 'APPROVED'
        }

    monkeypatch.setattr('auth_api.services.minio.MinioService._get_client', get_nr)


@pytest.fixture()
def staff_user_mock(monkeypatch):
    """Mock user_context."""

    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'username': 'staff user',
            'realm_access': {
                'roles': [
                    'staff',
                    'edit',
                    'create_accounts'
                ]
            }
        }

    def mock_auth():  # pylint: disable=unused-argument; mocks of library methods
        return 'test'

    monkeypatch.setattr('auth_api.utils.user_context._get_token', mock_auth)
    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', token_info)


@pytest.fixture()
def bceid_user_mock(monkeypatch):
    """Mock user_context."""

    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'username': 'CP1234567 user',
            'realm_access': {
                'roles': [
                    'edit',
                    'create_accounts'
                ]
            }
        }

    def mock_auth():  # pylint: disable=unused-argument; mocks of library methods
        return 'test'

    monkeypatch.setattr('auth_api.utils.user_context._get_token', mock_auth)
    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', token_info)


@pytest.fixture()
def system_user_mock(monkeypatch):
    """Mock user_context."""

    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {
            'username': 'staff user',
            'realm_access': {
                'roles': [
                    'staff',
                    'edit',
                    'system'
                ]
            }
        }

    def mock_auth():  # pylint: disable=unused-argument; mocks of library methods
        return 'test'

    monkeypatch.setattr('auth_api.utils.user_context._get_token', mock_auth)
    monkeypatch.setattr('auth_api.utils.user_context._get_token_info', token_info)


@pytest.fixture(autouse=True)
def mock_pub_sub_call(monkeypatch):
    """Mock pub sub call."""

    def publish(topic, message):
        return True

    monkeypatch.setattr('auth_api.services.gcp_queue.queue.publish', publish)
