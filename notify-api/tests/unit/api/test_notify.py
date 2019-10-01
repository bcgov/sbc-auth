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

"""Tests to verify the invitations API end-point.

Test-Suite to ensure that the /invitations endpoint is working as expected.
"""
import json
import os
from unittest.mock import patch

from notify_api import status as http_status
from notify_api.services import Notify as NotifyService


TEST_ORG_INFO = {
    'name': 'My Test Org'
}

TEST_JWT_CLAIMS = {
    'iss': os.getenv('JWT_OIDC_ISSUER'),
    'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
    'firstname': 'Test',
    'lastname': 'User',
    'preferred_username': 'testuser',
    'realm_access': {
        'roles': [
            'basic'
        ]
    }
}

TEST_JWT_HEADER = {
    'alg': os.getenv('JWT_OIDC_ALGORITHMS'),
    'typ': 'JWT',
    'kid': os.getenv('JWT_OIDC_AUDIENCE')
}


def factory_auth_header(jwt, claims):
    """Produce JWT tokens for use in tests."""
    return {'Authorization': 'Bearer ' + jwt.create_jwt(claims=claims, header=TEST_JWT_HEADER)}


def test_notify_post_success(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a notification can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }

    rv = client.post('/api/v1/notify', data=json.dumps(notify_info), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_201_CREATED


def test_notify_post_fail(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a notification post fail."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }

    with patch.object(NotifyService, 'create_notification', return_value=None) as mock_notify:
        rv = client.post('/api/v1/notify', data=json.dumps(notify_info), headers=headers,
                         content_type='application/json')
        assert rv.status_code == http_status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_notify.assert_called()


def test_notify_invalid_payload(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid notificaiton returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    notify_info = {
        'recipientEmail': 'test@abc.com'
    }
    rv = client.post('/api/v1/notify', data=json.dumps(notify_info),
                     headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_notify_without_token(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing a valid notificaiton without token returns a 401."""
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }
    rv = client.post('/api/v1/notify', data=json.dumps(notify_info), content_type='application/json')
    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_get_notification_by_id(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that a notificaiton can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    notify_info = {
        'notifyType': 'EMAIL',
        'requestDate': '2019-09-25T09:08:57.515479+00:00',
        'subject': 'test email',
        'recipients': 'test@abc.com',
        'contentBody': 'This is a test email from notify service.'
    }
    rv = client.post('/api/v1/notify', data=json.dumps(notify_info),
                     headers=headers, content_type='application/json')
    notify_dictionary = json.loads(rv.data)
    notification_id = notify_dictionary['id']
    rv = client.get('/api/v1/notify/{}'.format(notification_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_200_OK


def test_get_notification_not_exist_id(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that retrieving a notificaiton id that not exists returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    notification_id = 9999999
    rv = client.get('/api/v1/notify/{}'.format(notification_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND


def test_get_notification_invalid_id(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that retrieving a invalid notificaiton id returns a 500."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    notification_id = 'dfgd'
    rv = client.get('/api/v1/notify/{}'.format(notification_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_notification_without_id(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that retrieving notificaiton without id returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)
    notification_id = ''
    rv = client.get('/api/v1/notify/{}'.format(notification_id), headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_404_NOT_FOUND
