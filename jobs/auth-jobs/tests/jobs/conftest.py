# Copyright © 2026 Province of British Columbia
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
"""Common setup and fixtures for the py-test suite used by this service."""

import os
from pathlib import Path

import pytest
from flask_migrate import Migrate, upgrade
from sqlalchemy import event, text
from sqlalchemy_utils import create_database, database_exists, drop_database

from auth_api.models import db as _db
from auth_api.utils.logging import setup_logging
from invoke_jobs import create_app

AUTH_JOBS_DIR = Path(__file__).resolve().parents[2]
AUTH_API_MIGRATIONS_DIR = str(AUTH_JOBS_DIR.parent.parent / "auth-api" / "migrations")


@pytest.fixture(autouse=True)
def mock_pub_sub_call(mocker):
    """Mock pub sub call."""

    class Expando:
        """Expando class."""

    class PublisherMock:
        """Publisher Mock."""

        def __init__(self, *_args, **_kwargs):
            def result():
                """Return true for mock."""
                return True

            self.result = result

        def publish(self, *_args, **_kwargs):
            """Publish mock."""
            ex = Expando()
            ex.result = self.result
            return ex

    mocker.patch("google.cloud.pubsub_v1.PublisherClient", PublisherMock)


@pytest.fixture(scope="session")
def app():
    """Return a session-wide application configured in TEST mode."""
    return create_app("testing")


@pytest.fixture(scope="function")
def app_request():
    """Return a session-wide application configured in TEST mode."""
    return create_app("testing")


@pytest.fixture(scope="session")
def client(app):  # pylint: disable=redefined-outer-name
    """Return a session-wide Flask test client."""
    return app.test_client()


@pytest.fixture(scope="session", autouse=True)
def db(app):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a session-wide initialised database."""
    with app.app_context():
        if database_exists(_db.engine.url):
            drop_database(_db.engine.url)
        create_database(_db.engine.url)
        _db.session().execute(text('SET TIME ZONE "UTC";'))
        Migrate(app, _db, directory=AUTH_API_MIGRATIONS_DIR)
        upgrade()
        # Restore the logging, alembic and sqlalchemy have their own logging from alembic.ini.
        setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "logging.conf"))
        return _db


@pytest.fixture(scope="function", autouse=True)
def session(db, app):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a function-scoped session."""
    with app.app_context():
        with db.engine.connect() as conn:
            transaction = conn.begin()
            sess = db._make_scoped_session({"bind": conn})  # pylint: disable=protected-access
            # Establish SAVEPOINT (http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#using-savepoint)
            nested = sess.begin_nested()
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
