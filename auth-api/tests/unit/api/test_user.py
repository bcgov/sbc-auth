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

"""Tests to assure the user end-point.

Test-Suite to ensure that the /user endpoint is working as expected.
"""
import json

ADD_USER_REQUEST = {
   "username": "test11",
   "password": "1111",
   "firstname": "111",
   "lastname": "test",
   "email": "test11@gov.bc.ca",
   "enabled": True,
   "user_type": [
       "/test",
       "/basic/editor"
   ],
   "corp_type": "CP",
   "source": "PASSCODE"
}

USER_REQUEST = {
    'username': 'test11'
}

ADD_USER_REQUEST_SAME_EMAIL = {
   "username": "test12",
   "password": "1111",
   "firstname": "112",
   "lastname": "test",
   "email": "test11@gov.bc.ca",
   "enabled": True,
   "user_type": [
       "/test",
       "/basic/editor"
   ],
   "corp_type": "CP",
   "source": "PASSCODE"
}

def test_user_add_user_happy(client):
    """Assert that the endpoint returns 201."""
    rv = client.post('/api/v1/user', data=json.dumps(ADD_USER_REQUEST), content_type='application/json')
    assert rv.status_code == 201
    rv = client.delete('/api/v1/user', data=json.dumps(USER_REQUEST), content_type='application/json')


def test_user_add_user_sad(client):
    """Assert that the endpoint returns 500."""
    rv = client.post('/api/v1/user', data=json.dumps(ADD_USER_REQUEST), content_type='application/json')
    rv = client.post('/api/v1/user', data=json.dumps(ADD_USER_REQUEST_SAME_EMAIL), content_type='application/json')
    assert rv.status_code == 500
    rv = client.delete('/api/v1/user', data=json.dumps(USER_REQUEST), content_type='application/json')

def test_user_get_user_happy(client):
    """Assert that the endpoint returns 200."""
    rv = client.post('/api/v1/user', data=json.dumps(ADD_USER_REQUEST), content_type='application/json')
    rv = client.get('/api/v1/user', data=json.dumps(USER_REQUEST), content_type='application/json')
    assert rv.status_code == 200
    rv = client.delete('/api/v1/user', data=json.dumps(USER_REQUEST), content_type='application/json')


def test_user_get_user_sad(client):
    """Assert that the endpoint returns 500."""
    rv = client.get('/api/v1/user', data=json.dumps(USER_REQUEST), content_type='application/json')
    assert rv.status_code == 500


def test_user_delete_user_happy(client):
    """Assert that the endpoint returns 204."""
    rv = client.post('/api/v1/user', data=json.dumps(ADD_USER_REQUEST), content_type='application/json')
    rv = client.delete('/api/v1/user', data=json.dumps(USER_REQUEST), content_type='application/json')
    assert rv.status_code == 204


def test_user_delete_user_sad(client):
    """Assert that the endpoint returns 204."""
    rv = client.delete('/api/v1/user', data=json.dumps(USER_REQUEST), content_type='application/json')
    assert rv.status_code == 500
