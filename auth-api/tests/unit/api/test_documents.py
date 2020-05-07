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

"""Tests to assure the documents API end-point.

Test-Suite to ensure that the /documents endpoint is working as expected.
"""

from auth_api import status as http_status
from tests.utilities.factory_utils import factory_auth_header, factory_document_model
from tests.utilities.factory_scenarios import TestJwtClaims


def test_documents_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get documents endpoint returns 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get(f'/api/v1/documents/termsofuse', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('version_id') == '1'

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.anonymous_bcros_role)
    rv = client.get(f'/api/v1/documents/termsofuse', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('version_id') == 'd1'


def test_invalid_documents_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get documents endpoint returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get(f'/api/v1/documents/junk', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_404_NOT_FOUND
    assert rv.json.get('message') == 'The requested invitation could not be found.'


def test_documents_returns_200_for_some_type(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get documents endpoint with different type returns 200."""
    html_content = '<HTML></HTML>'
    version_id = '10'
    factory_document_model(version_id, 'sometype', html_content)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get(f'/api/v1/documents/sometype', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('content') == html_content
    assert rv.json.get('version_id') == version_id


def test_documents_returns_latest_always(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get documents endpoint returns latest version of document."""
    html_content_1 = '<HTML>1</HTML>'
    version_id_1 = '2'
    factory_document_model(version_id_1, 'termsofuse', html_content_1)

    html_content_2 = '<HTML>2</HTML>'
    version_id_2 = '3'
    factory_document_model(version_id_2, 'termsofuse', html_content_2)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get(f'/api/v1/documents/termsofuse', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('content') == html_content_2
    assert rv.json.get('version_id') == version_id_2

    version_id_3 = 'd3'
    factory_document_model(version_id_3, 'termsofuse_directorsearch', html_content_1)

    version_id_4 = 'd4'
    factory_document_model(version_id_4, 'termsofuse_directorsearch', html_content_2)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.anonymous_bcros_role)
    rv = client.get(f'/api/v1/documents/termsofuse', headers=headers, content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('content') == html_content_2
    assert rv.json.get('version_id') == version_id_4
