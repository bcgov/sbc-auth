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

"""The Unit Test for the API."""
from notify_api.db.models.notification import NotificationModel
from tests.utilities.factory_scenarios import (
    NOTIFICATION_DATA, NOTIFICATION_REQUEST_BAD_DATA, NOTIFICATION_REQUEST_DATA)


def test_get_by_id(session, app, client):  # pylint: disable=unused-argument
    """Assert the test can retrieve notification details by id."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)
    res = client.get('/api/v1/notify/{}'.format(notification.id))
    response_data = res.json()
    assert res.status_code == 200
    assert notification.recipients == response_data['recipients']


def test_get_by_id_not_found(session, app, client):  # pylint: disable=unused-argument
    """Assert the test cannot retrieve notification details with id not existing."""
    res = client.get('/api/v1/notify/{}'.format(int(1)))
    assert res.status_code == 404


def test_get_by_status(session, app, client):  # pylint: disable=unused-argument
    """Assert the test can retrieve notification details with status."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)
    res = client.get('/api/v1/notify/notifications/{}'.format(notification.status_code))
    response_data = res.json()
    assert res.status_code == 200
    assert notification.recipients == response_data[0]['recipients']


def test_post(session, app, client):  # pylint: disable=unused-argument
    """Assert the test can create notification."""
    for notification_data in NOTIFICATION_REQUEST_DATA:
        res = client.post('/api/v1/notify/', json=notification_data)
        assert res.status_code == 200

        response_data = res.json()
        notification = session.query(NotificationModel).get(response_data['id'])
        assert notification.id == response_data['id']


def test_post_with_bad_data(session, app, client):  # pylint: disable=unused-argument
    """Assert the test can not be create notification."""
    for notification_data in NOTIFICATION_REQUEST_BAD_DATA:
        res = client.post('/api/v1/notify/', json=notification_data)
        assert res.status_code == 400
