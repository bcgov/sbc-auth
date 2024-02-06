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

"""Tests to verify the orgs API end-point.

Test-Suite to ensure that the /orgs endpoint is working as expected.
"""
from faker import Faker

from auth_api import status as http_status
from auth_api.models import Org as OrgModel
from auth_api.utils.enums import OrgStatus, OrgType
from tests.utilities.factory_scenarios import TestJwtClaims
from tests.utilities.factory_utils import factory_auth_header


FAKE = Faker()


def assert_simple_org(result_dict: dict, org: OrgModel):
    """Assert simple org result."""
    assert result_dict['id'] == org.id
    assert result_dict['name'] == org.name
    assert result_dict['branchName'] == org.branch_name


def test_simple_org_search(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be searched using multiple syntax."""
    # Create active org

    org_inactive = OrgModel(name='INACTIVE TST ORG',
                            branch_name='INACTIVE TST BRANCH NAME',
                            type_code=OrgType.PREMIUM.value,
                            status_code=OrgStatus.INACTIVE.value).save()

    org_branch_1 = OrgModel(name='TST ORG NAME 1',
                            branch_name='TST BRANCH 1',
                            type_code=OrgType.PREMIUM.value,
                            status_code=OrgStatus.ACTIVE.value).save()

    org_branch_2 = OrgModel(name='TST ORG NAME 2',
                            branch_name='TST branch 2',
                            type_code=OrgType.PREMIUM.value,
                            status_code=OrgStatus.ACTIVE.value).save()

    org_no_branch_1 = OrgModel(name='TST ORG NO BRANCH Name 1',
                               type_code=OrgType.PREMIUM.value,
                               status_code=OrgStatus.ACTIVE.value).save()

    org_no_branch_2 = OrgModel(name='TST ORG NO BRANCH name 2',
                               type_code=OrgType.PREMIUM.value,
                               status_code=OrgStatus.ACTIVE.value).save()

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_eft_role)

    # Assert status filter by inactive orgs
    rv = client.get(f'/api/v1/orgs/simple?status={OrgStatus.INACTIVE.value}',
                    headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 1
    assert result['page'] == 1
    assert result['total'] == 1
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_inactive)

    # Assert default search - returns active orgs
    rv = client.get('/api/v1/orgs/simple', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 4
    assert result['page'] == 1
    assert result['total'] == 4
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_branch_1)
    assert_simple_org(result['items'][1], org_branch_2)
    assert_simple_org(result['items'][2], org_no_branch_1)
    assert_simple_org(result['items'][3], org_no_branch_2)

    # Assert search id
    rv = client.get(f'/api/v1/orgs/simple?id={org_no_branch_1.id}', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 1
    assert result['page'] == 1
    assert result['total'] == 1
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_no_branch_1)

    # Assert search id
    rv = client.get(f'/api/v1/orgs/simple?id={org_no_branch_1.id}', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 1
    assert result['page'] == 1
    assert result['total'] == 1
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_no_branch_1)

    # Assert search name
    rv = client.get('/api/v1/orgs/simple?name=Name 2', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 2
    assert result['page'] == 1
    assert result['total'] == 2
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_branch_2)
    assert_simple_org(result['items'][1], org_no_branch_2)

    # Assert search branch name
    rv = client.get('/api/v1/orgs/simple?branchName=branch', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 2
    assert result['page'] == 1
    assert result['total'] == 2
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_branch_1)
    assert_simple_org(result['items'][1], org_branch_2)

    # Assert search branch name
    rv = client.get('/api/v1/orgs/simple?branchName=ch 1', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 1
    assert result['page'] == 1
    assert result['total'] == 1
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_branch_1)

    # Assert search text with id
    rv = client.get(f'/api/v1/orgs/simple?searchText={org_no_branch_2.id}', headers=headers,
                    content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 1
    assert result['page'] == 1
    assert result['total'] == 1
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_no_branch_2)

    # Assert search text with name
    rv = client.get('/api/v1/orgs/simple?searchText=name 1', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 2
    assert result['page'] == 1
    assert result['total'] == 2
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_branch_1)
    assert_simple_org(result['items'][1], org_no_branch_1)

    # Assert search text with branch name
    rv = client.get('/api/v1/orgs/simple?searchText=ch 1', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 1
    assert result['page'] == 1
    assert result['total'] == 1
    assert result['limit'] == 10
    assert_simple_org(result['items'][0], org_branch_1)

    # Assert page 1
    rv = client.get('/api/v1/orgs/simple?page=1&limit=1', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 1
    assert result['page'] == 1
    assert result['total'] == 4
    assert result['limit'] == 1
    assert_simple_org(result['items'][0], org_branch_1)

    # Assert page 2
    rv = client.get('/api/v1/orgs/simple?page=2&limit=1', headers=headers, content_type='application/json')

    result = rv.json
    assert rv.status_code == http_status.HTTP_200_OK
    assert result['items']
    assert len(result['items']) == 1
    assert result['page'] == 2
    assert result['total'] == 4
    assert result['limit'] == 1
    assert_simple_org(result['items'][0], org_branch_2)
