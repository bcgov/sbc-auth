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
import logging

from notify_api.db.models.notification import NotificationModel
from tests.factories.content import ContentFactory
from tests.factories.jwt import JwtClaimsFactory, JwtFactory
from tests.factories.notification import NotificationFactory


logger = logging.getLogger(__name__)


def test_get_by_id_no_token(session, app, client):  # pylint: disable=unused-argument
    """Assert the test cannot retrieve notification details with no token."""
    notification = NotificationFactory.create_model(session)

    res = client.get('/api/v1/notify/{}'.format(notification.id))
    assert res.status_code == 403


def test_get_by_id(session, app, client, jwt):  # pylint: disable=unused-argument
    """Assert the test can retrieve notification details by id."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)
    ContentFactory.create_model(session, notification.id, content_info=ContentFactory.Models.CONTENT_1)

    headers = JwtFactory.factory_auth_header(jwt=jwt, claims=JwtClaimsFactory.public_user_role)
    res = client.get('/api/v1/notify/{}'.format(notification.id), headers=headers)
    response_data = res.json()
    assert res.status_code == 200
    assert response_data['recipients'] == NotificationFactory.Models.PENDING_1['recipients']
    assert response_data['content']['subject'] == ContentFactory.Models.CONTENT_1['subject']


def test_get_by_id_not_found(session, app, client, jwt):  # pylint: disable=unused-argument
    """Assert the test cannot retrieve notification details with id not existing."""
    headers = JwtFactory.factory_auth_header(jwt=jwt, claims=JwtClaimsFactory.public_user_role)
    res = client.get('/api/v1/notify/{}'.format(int(1000)), headers=headers)
    assert res.status_code == 404


def test_get_by_status(session, app, client, jwt):  # pylint: disable=unused-argument
    """Assert the test can retrieve notification details with status."""
    notification = NotificationFactory.create_model(session, notification_info=NotificationFactory.Models.PENDING_1)
    ContentFactory.create_model(session, notification.id, content_info=ContentFactory.Models.CONTENT_1)

    headers = JwtFactory.factory_auth_header(jwt=jwt, claims=JwtClaimsFactory.public_user_role)
    res = client.get('/api/v1/notify/notifications/{}'.format(notification.status_code), headers=headers)
    response_data = res.json()
    assert res.status_code == 200
    assert response_data[0]['recipients'] == NotificationFactory.Models.PENDING_1['recipients']
    assert response_data[0]['content']['subject'] == ContentFactory.Models.CONTENT_1['subject']


def test_post(session, app, client, client_id, stan_server, jwt):  # pylint: disable=unused-argument, too-many-arguments
    """Assert the test can create notification."""
    headers = JwtFactory.factory_auth_header(jwt=jwt, claims=JwtClaimsFactory.public_user_role)
    for notification_data in list(NotificationFactory.RequestData):
        res = client.post('/api/v1/notify/', json=notification_data, headers=headers)
        assert res.status_code == 200

        response_data = res.json()
        notification = session.query(NotificationModel).get(response_data['id'])
        assert notification.id == response_data['id']
        assert notification.recipients == response_data['recipients']
        assert notification.content.subject == response_data['content']['subject']


def test_post_with_bad_data(session, app, jwt, client):  # pylint: disable=unused-argument
    """Assert the test can not be create notification."""
    headers = JwtFactory.factory_auth_header(jwt=jwt, claims=JwtClaimsFactory.public_user_role)
    for notification_data in list(NotificationFactory.RequestBadData):
        res = client.post('/api/v1/notify/', json=notification_data, headers=headers)
        assert res.status_code == 400
