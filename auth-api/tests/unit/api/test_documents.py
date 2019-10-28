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

import copy
import json
import uuid

from auth_api import status as http_status

from tests.utilities.factory_utils import (
    factory_affiliation_model, factory_auth_header, factory_entity_model, factory_membership_model, factory_org_model,
    factory_user_model,factory_document_model)


def test_documents_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for affiliated users returns 200."""
    html_content = '<HTML></HTML>'
    version_id = 1
    document = factory_document_model(version_id,'termsofuse',html_content)

    rv = client.get(f'/api/v1/documents/termsofuse',content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('content') == html_content
    assert rv.json.get('version_id') == version_id

def test_documents_returns_latest_always(client, jwt, session):  # pylint:disable=unused-argument
    """Assert authorizations for affiliated users returns 200."""
    html_content_1 = '<HTML>1</HTML>'
    version_id_1 = 1
    document_1 = factory_document_model(version_id_1,'termsofuse',html_content_1)

    html_content_2 = '<HTML>2</HTML>'
    version_id_2 = 2
    document_2 = factory_document_model(version_id_2, 'termsofuse', html_content_2)

    rv = client.get(f'/api/v1/documents/termsofuse',content_type='application/json')

    assert rv.status_code == http_status.HTTP_200_OK
    assert rv.json.get('content') == html_content_2
    assert rv.json.get('version_id') == version_id_2