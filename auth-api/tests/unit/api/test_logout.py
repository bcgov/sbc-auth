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

"""Tests to assure the token end-point.

Test-Suite to ensure that the /token endpoint is working as expected.
"""

# import json

# from auth_api import status as http_status
# from auth_api.exceptions.errors import Error


# TOKEN_REQUEST = {
#     'username': 'test11',
#     'password': '1111'
# }


# def test_logout(client):
#     """Assert that the endpoint returns 200."""
#     # Add user
#     rv = client.post('/api/v1/admin/users', data=json.dumps(TOKEN_REQUEST), content_type='application/json')
#     # Get refresh token
#     rv = client.post('/api/v1/token', data=json.dumps(TOKEN_REQUEST), content_type='application/json')
#     refresh_token = {'refresh_token': json.loads(rv.data.decode('utf-8')).get('refresh_token')}
#     # Logout
#     rv = client.post('/api/v1/logout', data=json.dumps(refresh_token), content_type='application/json')
#     assert rv.status_code == http_status.HTTP_204_NO_CONTENT
#     # Delete user
#     rv = client.delete('/api/v1/admin/users', data=json.dumps(TOKEN_REQUEST), content_type='application/json')


# def test_logout_invalid_token(client):
#     """Assert that the endpoint returns bad request."""
#     # Add user
#     rv = client.post('/api/v1/admin/users', data=json.dumps(TOKEN_REQUEST), content_type='application/json')
#     # Get refresh token
#     rv = client.post('/api/v1/token', data=json.dumps(TOKEN_REQUEST), content_type='application/json')
#     refresh_token = {'refresh_token': json.loads(rv.data.decode('utf-8')).get('access_token')}
#     # Logout
#     rv = client.post('/api/v1/logout', data=json.dumps(refresh_token), content_type='application/json')
#     assert rv.status_code == Error.INVALID_REFRESH_TOKEN.status_code
#     # Delete user
#     rv = client.delete('/api/v1/admin/users', data=json.dumps(TOKEN_REQUEST), content_type='application/json')
