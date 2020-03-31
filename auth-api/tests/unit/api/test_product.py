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


def test_get_all_products(client, session):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved via GET."""
    rv = client.get('/api/v1/products')
    item_list = json.loads(rv.data)
    # assert the structure is correct by checking for name, description properties in each element
    for item in item_list:
        assert item['name'] and item['description']
