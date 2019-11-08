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

"""Tests to assure the status end-point."""


def test_status_with_name(client):
    """Assert that the endpoint returns 200 with actual result."""
    service_name = 'PAYBC'

    rv = client.get(f'/api/v1/status/{service_name}')
    assert rv.status_code == 200


def test_status_without_name(client):
    """Assert that the endpoint returns 404."""
    rv = client.get(f'/api/v1/status/')
    assert rv.status_code == 404


def test_status_with_name_not_exists(client):
    """Assert that the endpoint returns 200 without result."""
    service_name = 'PAYBC1'

    rv = client.get(f'/api/v1/status/{service_name}')
    assert rv.status_code == 200
