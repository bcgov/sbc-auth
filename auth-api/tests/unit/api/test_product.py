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
"""Tests for the Product resource.

Test suite to ensure that the Product api endpoints are working as expected.
"""

import json

from auth_api.schemas import utils as schema_utils


def test_get_all_products(client, session):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved via GET."""
    rv = client.get('/api/v1/products')
    item_list = json.loads(rv.data)

    assert schema_utils.validate(item_list, 'products')[0]
    # assert the structure is correct by checking for name, description properties in each element
    mhr_sub_prods = ['MHR_QSLN', 'MHR_QSHM', 'MHR_QSHD']
    for item in item_list:
        assert item['code'] and item['description']
        if item['code'] in mhr_sub_prods:
            assert item['parentCode'] == 'MHR'
            assert item['keycloak_group']
        else:
            assert not item.get('parentCode')
