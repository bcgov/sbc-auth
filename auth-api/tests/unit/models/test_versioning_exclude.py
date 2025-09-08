# Copyright © 2025 Province of British Columbia
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
# See the specific language governing permissions and
# limitations under the License.

"""Tests to assure the Versioning functionality.

Test-Suite to ensure that the Versioned class works as expected with column exclusions.
"""

from datetime import datetime, timedelta, timezone

from sql_versioning import versioned_session

from auth_api.models import User


def test_versioned_excludes_columns_in_create_version(session):
    """Test that excluded columns are not processed during version creation."""
    versioned_session(session)

    user = User(
        username="testuser",
        keycloak_guid="1b20db59-19a0-4727-affe-c6f64309fd04",
        firstname="John",
        lastname="Doe",
        modified=datetime.now(tz=timezone.utc),
        login_time=datetime.now(tz=timezone.utc),
    )

    session.add(user)
    session.commit()

    # modified, login_time, modified_by_id, modified_by, created are excluded.
    user.modified = datetime.now(tz=timezone.utc) + timedelta(seconds=1)
    user.login_time = datetime.now(tz=timezone.utc) + timedelta(seconds=1)
    user.modified_by_id = 1
    user.created = datetime.now(tz=timezone.utc)

    session.flush()
    session.commit()

    history_cls = User.__history_mapper__.class_
    history_records = session.query(history_cls).all()

    assert len(history_records) == 0

    # this should cause a trigger version
    user.firstname = "Jane"
    session.flush()
    session.commit()

    history_records = session.query(history_cls).all()

    assert len(history_records) == 1
    history_record = history_records[0]
    assert history_record.firstname == "John"

    # we need these fields, but they should not be triggered upon
    assert history_record.modified
    assert history_record.login_time
    assert history_record.modified_by_id
    assert history_record.modified_by
    assert history_record.created
