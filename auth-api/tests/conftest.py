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
from concurrent.futures import CancelledError
from unittest.mock import MagicMock, patch

import pytest
from flask_migrate import Migrate, upgrade
from sqlalchemy import event, text

from auth_api import create_app, setup_jwt_manager
from auth_api.exceptions import BusinessException, Error
from auth_api.models import db as _db
from auth_api.utils.auth import jwt as _jwt


def find_subpath(root_dir, target_subpath):
    """Auxiliary subpath search function."""
    for root, dirs, files in os.walk(root_dir):
        if target_subpath in os.path.join(root, "").replace("\\", "/"):  # Ensure cross-platform compatibility
            return os.path.join(root, "")
    return None


def mock_token(config_id="", config_secret=""):
    """Mock token generator."""
    return "TOKEN...."


@pytest.fixture(scope="session", autouse=True)
def app():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app("testing")

    return _app


@pytest.fixture(scope="function", autouse=True)
def app_request():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app("testing")

    return _app


@pytest.fixture(scope="function", autouse=True)
def global_http_origin(app):
    """Set a global HTTP_ORIGIN for all tests."""
    with app.test_request_context("/", environ_base={"HTTP_ORIGIN": "https://test.com"}):
        yield


@pytest.fixture(scope="session")
def client(app):  # pylint: disable=redefined-outer-name
    """Return a session-wide Flask test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def jwt():
    """Return a session-wide jwt manager."""
    return _jwt


@pytest.fixture(scope="session")
def client_ctx(app):  # pylint: disable=redefined-outer-name
    """Return session-wide Flask test client."""
    with app.test_client() as _client:
        yield _client


@pytest.fixture(scope="session")
def db(app):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a session-wide initialised database.

    Drops all existing tables - Meta follows Postgres FKs
    """
    with app.app_context():
        drop_schema_sql = text(
            """
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            GRANT ALL ON SCHEMA public TO postgres;
            GRANT ALL ON SCHEMA public TO public;
        """
        )

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

        root_directory = os.pardir
        target_subpath = "auth-api/migrations"

        result = find_subpath(root_directory, target_subpath)

        if not result:
            root_directory = "/home/runner"
            result = find_subpath(root_directory, target_subpath)

        Migrate(app, _db, directory=result)
        upgrade()

        return _db


@pytest.fixture(scope="function")
def session(db, app):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a function-scoped session."""
    with app.app_context():
        with db.engine.connect() as conn:
            transaction = conn.begin()
            sess = db._make_scoped_session(dict(bind=conn))  # pylint: disable=protected-access
            # Establish SAVEPOINT (http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#using-savepoint)
            nested = sess.begin_nested()
            old_session = db.session
            db.session = sess
            db.session.commit = nested.commit
            db.session.rollback = nested.rollback

            @event.listens_for(sess, "after_transaction_end")
            def restart_savepoint(sess2, trans):  # pylint: disable=unused-variable
                nonlocal nested
                if trans.nested:
                    # Handle where test DOESN'T session.commit()
                    sess2.expire_all()
                    nested = sess.begin_nested()
                    # When using a SAVEPOINT via the Session.begin_nested() or Connection.begin_nested() methods,
                    # the transaction object returned must be used to commit or rollback the SAVEPOINT.
                    # Calling the Session.commit() or Connection.commit() methods will always commit the
                    # outermost transaction; this is a SQLAlchemy 2.0 specific behavior that is
                    # reversed from the 1.x series
                    db.session = sess
                    db.session.commit = nested.commit
                    db.session.rollback = nested.rollback

            try:
                yield db.session
            finally:
                db.session.remove()
                transaction.rollback()
                event.remove(sess, "after_transaction_end", restart_savepoint)
                db.session = old_session


@pytest.fixture(scope="session", autouse=True)
def auto(docker_services, app):
    """Spin up a keycloak instance and initialize jwt."""
    if app.config["USE_TEST_KEYCLOAK_DOCKER"]:
        docker_services.start("keycloak")
        docker_services.wait_for_service("keycloak", 8081, timeout=60.0)

    setup_jwt_manager(app, _jwt)

    if app.config["USE_DOCKER_MOCK"]:
        docker_services.start("gcs-emulator")
        docker_services.start("notify")
        docker_services.start("bcol")
        docker_services.start("pay")
        docker_services.start("proxy")
        time.sleep(10)


@pytest.fixture(scope="session")
def docker_compose_files(pytestconfig):
    """Get the docker-compose.yml absolute path."""
    import os

    return [os.path.join(str(pytestconfig.rootdir), "tests/docker", "docker-compose.yml")]


@pytest.fixture()
def auth_mock(monkeypatch):
    """Mock check_auth."""
    monkeypatch.setattr("auth_api.services.entity.check_auth", lambda *args, **kwargs: None)
    monkeypatch.setattr("auth_api.services.org.check_auth", lambda *args, **kwargs: None)
    monkeypatch.setattr("auth_api.services.invitation.check_auth", lambda *args, **kwargs: None)
    monkeypatch.setattr("auth_api.services.affiliation_invitation.check_auth", lambda *args, **kwargs: None)


@pytest.fixture()
def notify_mock(monkeypatch):
    """Mock send_email."""
    monkeypatch.setattr("auth_api.services.invitation.send_email", lambda *args, **kwargs: None)
    monkeypatch.setattr("auth_api.services.affiliation_invitation.send_email", lambda *args, **kwargs: None)


@pytest.fixture()
def notify_org_mock(monkeypatch):
    """Mock send_email."""
    monkeypatch.setattr("auth_api.services.org.send_email", lambda *args, **kwargs: None)


@pytest.fixture()
def keycloak_mock(monkeypatch):
    """Mock keycloak services."""
    monkeypatch.setattr(
        "auth_api.services.keycloak.KeycloakService.join_account_holders_group", lambda *args, **kwargs: None
    )
    monkeypatch.setattr("auth_api.services.keycloak.KeycloakService.join_users_group", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "auth_api.services.keycloak.KeycloakService.remove_from_account_holders_group", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        "auth_api.services.keycloak.KeycloakService.add_or_remove_product_keycloak_groups", lambda *args, **kwargs: None
    )


@pytest.fixture()
def business_exception_mock(monkeypatch):
    """Mock get business call exceotion."""

    def get_business(business_identifier, token):
        raise BusinessException(Error.AFFILIATION_INVITATION_BUSINESS_NOT_FOUND, None)

    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.AffiliationInvitation._get_business_details", get_business
    )


@pytest.fixture()
def business_mock(monkeypatch):
    """Mock get business call."""

    def get_business(business_identifier, token):
        return {"business": {"identifier": "CP0002103", "legalName": "BarFoo, Inc.", "legalType": "CP"}}

    def get_businesses(business_identifiers, token):
        return [
            {
                "identifier": "CP0002103",
                "legalName": "BarFoo, Inc.",
                "legalType": "CP",
                "state": "ACTIVE",
            },
            {
                "identifier": "CP0002104",
                "legalName": "BarFooMeToo, Inc.",
                "legalType": "CP",
                "state": "ACTIVE",
            },
        ]

    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.AffiliationInvitation._get_business_details", get_business
    )

    monkeypatch.setattr(
        "auth_api.services.affiliation_invitation.AffiliationInvitation._get_multiple_business_details", get_businesses
    )


@pytest.fixture()
def nr_mock(monkeypatch):
    """Mock nr get call."""

    def get_nr(business_identifier):
        return {
            "applicants": {"emailAddress": "test@test.com", "phoneNumber": "1112223333"},
            "names": [{"name": "TEST INC..", "state": "APPROVED"}],
            "state": "APPROVED",
            "requestTypeCd": "BC",
        }

    monkeypatch.setattr("auth_api.services.affiliation.Affiliation._get_nr_details", get_nr)


@pytest.fixture()
def gcs_mock(monkeypatch):
    """Mock Google Cloud Storage client and blob using monkeypatch."""
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Set up the mock chain
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.generate_signed_url.return_value = "http://mocked.url"

    # Monkeypatch the storage.Client to return the mock client
    monkeypatch.setattr("auth_api.services.google_store.storage.Client", lambda: mock_client)

    yield {
        "mock_client": mock_client,
        "mock_bucket": mock_bucket,
        "mock_blob": mock_blob,
    }


@pytest.fixture()
def staff_user_mock(monkeypatch):
    """Mock user_context."""

    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {"username": "staff user", "realm_access": {"roles": ["staff", "edit", "create_accounts"]}}

    def mock_auth():  # pylint: disable=unused-argument; mocks of library methods
        return "test"

    monkeypatch.setattr("auth_api.utils.user_context._get_token", mock_auth)
    monkeypatch.setattr("auth_api.utils.user_context._get_token_info", token_info)


@pytest.fixture()
def bceid_user_mock(monkeypatch):
    """Mock user_context."""

    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {"username": "CP1234567 user", "realm_access": {"roles": ["edit", "create_accounts"]}}

    def mock_auth():  # pylint: disable=unused-argument; mocks of library methods
        return "test"

    monkeypatch.setattr("auth_api.utils.user_context._get_token", mock_auth)
    monkeypatch.setattr("auth_api.utils.user_context._get_token_info", token_info)


@pytest.fixture()
def system_user_mock(monkeypatch):
    """Mock user_context."""

    def token_info():  # pylint: disable=unused-argument; mocks of library methods
        return {"username": "staff user", "realm_access": {"roles": ["staff", "edit", "system"]}}

    def mock_auth():  # pylint: disable=unused-argument; mocks of library methods
        return "test"

    monkeypatch.setattr("auth_api.utils.user_context._get_token", mock_auth)
    monkeypatch.setattr("auth_api.utils.user_context._get_token_info", token_info)


@pytest.fixture(autouse=True)
def mock_pub_sub_call(mocker):
    """Mock pub sub call."""

    class PublisherMock:
        """Publisher Mock."""

        def __init__(self, *args, **kwargs):
            pass

        def publish(self, *args, **kwargs):
            """Publish mock."""
            raise CancelledError("This is a mock")

    mocker.patch("google.cloud.pubsub_v1.PublisherClient", PublisherMock)
