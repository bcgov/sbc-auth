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
"""Tests for the Affiliation service.

Test suite to ensure that the Affiliation service routines are working as expected.
"""
from unittest.mock import ANY, patch

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.dataclass import Activity
from auth_api.models.dataclass import Affiliation as AffiliationData
from auth_api.models.dataclass import DeleteAffiliationRequest
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.org import Org as OrgModel
from auth_api.services import ActivityLogPublisher
from auth_api.services import Affiliation as AffiliationService
from auth_api.utils.enums import ActivityAction, OrgType
from tests.utilities.factory_scenarios import TestEntityInfo, TestJwtClaims, TestOrgInfo, TestOrgTypeInfo, TestUserInfo
from tests.utilities.factory_utils import (
    convert_org_to_staff_org, factory_entity_service, factory_membership_model, factory_org_service,
    factory_user_model_with_contact, patch_get_firms_parties, patch_token_info)


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation(session, auth_mock, monkeypatch, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id, business_identifier, environment,
                                                        TestEntityInfo.entity_lear_mock['passCode'])
    assert affiliation
    assert affiliation.entity.identifier == entity_service.identifier
    assert affiliation.as_dict()['organization']['id'] == org_dictionary['id']


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_no_org(session, auth_mock, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created without org."""
    entity_service = factory_entity_service()
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(None, business_identifier, environment)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_no_entity(session, auth_mock, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created without entity."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(org_id, None, environment)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_implicit(session, auth_mock, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created when org is BASIC."""
    entity_service1 = factory_entity_service()
    entity_dictionary1 = entity_service1.as_dict()
    business_identifier1 = entity_dictionary1['business_identifier']

    org_service = factory_org_service(org_type_info=TestOrgTypeInfo.implicit)
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    pass_code = '111111111'

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(org_id, business_identifier1, environment, pass_code)

        found_org = OrgModel.query.filter_by(id=org_id).first()
        assert found_org is None

    assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_with_passcode(session, auth_mock, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id,
                                                        business_identifier,
                                                        environment,
                                                        TestEntityInfo.entity_lear_mock['passCode'])
    assert affiliation
    assert affiliation.entity.identifier == entity_service.identifier
    assert affiliation.as_dict()['organization']['id'] == org_dictionary['id']


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_with_passcode_no_passcode_input(session,
                                                            auth_mock,
                                                            environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be created with a passcode entity and no passcode input parameter."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_passcode)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(org_id, business_identifier, environment)

    assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_exists(session, auth_mock, environment):  # pylint:disable=unused-argument
    """Assert that multiple affiliation is allowed."""
    entity_service1 = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary1 = entity_service1.as_dict()
    business_identifier1 = entity_dictionary1['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    org_service_2 = factory_org_service(org_info=TestOrgInfo.org2)
    org_dictionary_2 = org_service_2.as_dict()
    org_id_2 = org_dictionary_2['id']

    pass_code = TestEntityInfo.entity_lear_mock['passCode']

    # create first row in affiliation table
    AffiliationService.create_affiliation(org_id, business_identifier1, environment, pass_code)

    affiliation = AffiliationService.create_affiliation(org_id_2, business_identifier1, environment, pass_code)

    assert affiliation


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_firms(session, auth_mock, monkeypatch, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    patch_get_firms_parties(monkeypatch)
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock3)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id, business_identifier, environment,
                                                        TestEntityInfo.entity_lear_mock3['passCode'])
    assert affiliation
    assert affiliation.entity.identifier == entity_service.identifier
    assert affiliation.as_dict()['organization']['id'] == org_dictionary['id']


@pytest.mark.parametrize('test_name, org_type, should_succeed, environment', [
    ('sbc_staff_create_affiliation_no_passcode_success', OrgType.SBC_STAFF.value, True, None),
    ('staff_create_affiliation_no_passcode_success', OrgType.STAFF.value, True, 'Test'),
    ('premium_create_affiliation_failure', OrgType.PREMIUM.value, False, None)
])
def test_create_affiliation_staff_sbc_staff(
    session, auth_mock, monkeypatch, test_name: str, org_type: OrgType, should_succeed: bool, environment: str
):  # pylint:disable=unused-argument
    """Assert Staff or SBC staff can create an affiliation, without passcode."""
    db_user = factory_user_model_with_contact(user_info=TestUserInfo.user_test)
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock3)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    factory_membership_model(db_user.id, org_id)

    # We can't create an org with SBC_STAFF or STAFF intentionally for security purposes.
    if org_type in [OrgType.SBC_STAFF.value, OrgType.STAFF.value]:
        convert_org_to_staff_org(org_id, org_type)

    # Requires staff role.
    user = TestJwtClaims.staff_role if org_type == OrgType.STAFF.value \
        else TestJwtClaims.public_bceid_account_holder_user
    user['idp_userid'] = db_user.idp_userid
    user['sub'] = db_user.keycloak_guid
    patch_token_info(user, monkeypatch)

    if should_succeed:
        affiliation = AffiliationService.create_affiliation(org_id, business_identifier, environment)
        assert affiliation
        assert affiliation.entity.identifier == entity_service.identifier
        assert affiliation.as_dict()['organization']['id'] == org_dictionary['id']
    else:
        with pytest.raises(BusinessException):
            affiliation = AffiliationService.create_affiliation(org_id, business_identifier, environment)


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_firms_party_with_additional_space(session, auth_mock,
                                                              monkeypatch, environment):
    """Assert that an Affiliation can be created."""
    patch_get_firms_parties(monkeypatch)
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock3)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    # When party name has additional space
    pass_code = TestEntityInfo.entity_lear_mock3['passCode'].replace(' ', '  ')
    affiliation = AffiliationService.create_affiliation(org_id, business_identifier, environment,
                                                        pass_code)
    assert affiliation
    assert affiliation.entity.identifier == entity_service.identifier
    assert affiliation.as_dict()['organization']['id'] == org_dictionary['id']


@pytest.mark.parametrize('environment', ['test', None])
def test_create_affiliation_firms_party_not_valid(session, auth_mock, monkeypatch,
                                                  environment):
    """Assert that an Affiliation can be created."""
    patch_get_firms_parties(monkeypatch)
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock3)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    with pytest.raises(BusinessException) as exception:
        AffiliationService.create_affiliation(org_id, business_identifier, environment, 'test user')

    assert exception.value.code == Error.INVALID_USER_CREDENTIALS.name


@pytest.mark.parametrize('environment', ['test', None])
def test_find_affiliated_entities_by_org_id(session, auth_mock, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    entity_service1 = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary1 = entity_service1.as_dict()
    business_identifier1 = entity_dictionary1['business_identifier']

    entity_service2 = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock2)
    entity_dictionary2 = entity_service2.as_dict()
    business_identifier2 = entity_dictionary2['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    # create first row in affiliation table
    AffiliationService.create_affiliation(org_id,
                                          business_identifier1,
                                          environment,
                                          TestEntityInfo.entity_lear_mock['passCode'])
    # create second row in affiliation table
    AffiliationService.create_affiliation(org_id,
                                          business_identifier2,
                                          environment,
                                          TestEntityInfo.entity_lear_mock2['passCode'])

    affiliated_entities = AffiliationService.find_visible_affiliations_by_org_id(org_id, environment)

    assert affiliated_entities
    assert len(affiliated_entities) == 2
    assert affiliated_entities[0]['business_identifier'] == entity_dictionary2['business_identifier']


@pytest.mark.parametrize('environment', ['test', None])
def test_find_affiliated_entities_by_org_id_no_org(session, auth_mock, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be find without org id or org id not exists."""
    with pytest.raises(BusinessException) as exception:
        AffiliationService.find_visible_affiliations_by_org_id(None, environment)
    assert exception.value.code == Error.DATA_NOT_FOUND.name

    with pytest.raises(BusinessException) as exception:
        AffiliationService.find_visible_affiliations_by_org_id(999999, environment)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


@pytest.mark.parametrize('environment', ['test', None])
def test_find_affiliated_entities_by_org_id_no_affiliation(session, auth_mock,
                                                           environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can not be find without affiliation."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    with patch.object(AffiliationModel, 'find_affiliations_by_org_id', return_value=[]):
        affiliations = AffiliationService.find_visible_affiliations_by_org_id(org_id, environment)
        assert not affiliations


@pytest.mark.parametrize('environment', ['test', None])
def test_delete_affiliation(session, auth_mock, monkeypatch, environment):  # pylint:disable=unused-argument
    """Assert that an affiliation can be deleted."""
    entity_service = factory_entity_service(TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']
    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        affiliation = AffiliationService.create_affiliation(org_id,
                                                            business_identifier,
                                                            environment,
                                                            TestEntityInfo.entity_lear_mock['passCode'])
        mock_alp.assert_called_with(Activity(action=ActivityAction.CREATE_AFFILIATION.value,
                                             org_id=ANY, name=ANY, id=ANY))

    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None) as mock_alp:
        delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=business_identifier)
        AffiliationService.delete_affiliation(delete_affiliation_request, environment=environment)
        mock_alp.assert_called_with(Activity(action=ActivityAction.REMOVE_AFFILIATION.value,
                                             org_id=ANY, name=ANY, id=ANY))

    found_affiliation = AffiliationModel.query.filter_by(id=affiliation.identifier).first()
    assert found_affiliation is None


@pytest.mark.parametrize('environment', ['test', None])
def test_delete_affiliation_no_org(session, auth_mock, monkeypatch, environment):  # pylint:disable=unused-argument
    """Assert that an affiliation can not be deleted without org."""
    entity_service = factory_entity_service(TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    patch_token_info(TestJwtClaims.user_test, monkeypatch)

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    AffiliationService.create_affiliation(org_id,
                                          business_identifier,
                                          environment,
                                          TestEntityInfo.entity_lear_mock['passCode'])

    with pytest.raises(BusinessException) as exception:
        delete_affiliation_request = DeleteAffiliationRequest(org_id=None, business_identifier=business_identifier)
        AffiliationService.delete_affiliation(delete_affiliation_request, environment=environment)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


@pytest.mark.parametrize('environment', ['test', None])
def test_delete_affiliation_no_entity(session, auth_mock, monkeypatch, environment):  # pylint:disable=unused-argument
    """Assert that an affiliation can not be deleted without entity."""
    entity_service = factory_entity_service(TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    patch_token_info(TestJwtClaims.user_test, monkeypatch)

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    AffiliationService.create_affiliation(org_id,
                                          business_identifier,
                                          environment,
                                          TestEntityInfo.entity_lear_mock['passCode'])

    with pytest.raises(BusinessException) as exception:
        delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=None)
        AffiliationService.delete_affiliation(delete_affiliation_request, environment=environment)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


@pytest.mark.parametrize('environment', ['test', None])
def test_delete_affiliation_no_affiliation(session, auth_mock, monkeypatch,
                                           environment):  # pylint:disable=unused-argument
    """Assert that an affiliation can not be deleted without affiliation."""
    entity_service = factory_entity_service(TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    patch_token_info(TestJwtClaims.user_test, monkeypatch)

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    AffiliationService.create_affiliation(org_id,
                                          business_identifier,
                                          environment,
                                          TestEntityInfo.entity_lear_mock['passCode'])
    delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=business_identifier)
    AffiliationService.delete_affiliation(delete_affiliation_request, environment=environment)

    with pytest.raises(BusinessException) as exception:
        delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=business_identifier)
        AffiliationService.delete_affiliation(delete_affiliation_request, environment=environment)

    assert exception.value.code == Error.DATA_NOT_FOUND.name


@pytest.mark.parametrize('environment', ['test', None])
def test_delete_affiliation_implicit(session, auth_mock, monkeypatch, environment):  # pylint:disable=unused-argument
    """Assert that an affiliation can be deleted."""
    entity_service = factory_entity_service(TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service(org_type_info=TestOrgTypeInfo.implicit)
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    patch_token_info(TestJwtClaims.user_test, monkeypatch)

    affiliation = AffiliationService.create_affiliation(org_id,
                                                        business_identifier,
                                                        environment,
                                                        TestEntityInfo.entity_lear_mock['passCode'])
    delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=business_identifier)
    AffiliationService.delete_affiliation(delete_affiliation_request, environment=environment)

    found_affiliation = AffiliationModel.query.filter_by(id=affiliation.identifier).first()
    assert found_affiliation is None


@pytest.mark.parametrize('environment', ['test', None])
def test_delete_affiliation_reset_passcode(session, auth_mock, monkeypatch,
                                           environment):  # pylint:disable=unused-argument
    """Assert that an affiliation can be deleted."""
    entity_service = factory_entity_service(TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    patch_token_info(TestJwtClaims.public_account_holder_user, monkeypatch)

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation = AffiliationService.create_affiliation(org_id,
                                                        business_identifier,
                                                        environment,
                                                        TestEntityInfo.entity_lear_mock['passCode'])
    delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=business_identifier,
                                                          email_addresses=None, reset_passcode=True)
    AffiliationService.delete_affiliation(delete_affiliation_request, environment=environment)

    found_affiliation = AffiliationModel.query.filter_by(id=affiliation.identifier).first()
    assert found_affiliation is None


def test_create_new_business(session, auth_mock, nr_mock):  # pylint:disable=unused-argument
    """Assert that an new business can be created."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()

    affiliation_data = AffiliationData(org_id=org_dictionary['id'], business_identifier='NR 1234567',
                                       email='test@test.com', phone='1112223333')

    affiliation = AffiliationService.create_new_business_affiliation(affiliation_data)
    assert affiliation
    assert affiliation.as_dict()['business']['business_identifier'] == affiliation_data.business_identifier


def test_create_new_business_email_case(session, auth_mock, nr_mock):  # pylint:disable=unused-argument
    """Assert that a new business can be created."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()

    affiliation_data = AffiliationData(org_id=org_dictionary['id'], business_identifier='NR 1234567',
                                       email='TEST@TEST.COM', phone='1112223333')

    affiliation = AffiliationService.create_new_business_affiliation(affiliation_data)
    assert affiliation
    assert affiliation.as_dict()['business']['business_identifier'] == affiliation_data.business_identifier


def test_create_new_business_invalid_contact(session, auth_mock, nr_mock):  # pylint:disable=unused-argument
    """Assert that an new business can be created."""
    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()

    affiliation_data = AffiliationData(org_id=org_dictionary['id'], business_identifier='NR 1234567')

    with pytest.raises(BusinessException) as exception:
        affiliation_data.phone = '0000000000'
        AffiliationService.create_new_business_affiliation(affiliation_data)

    assert exception.value.code == Error.NR_INVALID_CONTACT.name

    with pytest.raises(BusinessException) as exception:
        affiliation_data.phone = None
        affiliation_data.email = 'aaa@aaa.com'
        AffiliationService.create_new_business_affiliation(affiliation_data)

    assert exception.value.code == Error.NR_INVALID_CONTACT.name


def test_find_affiliations_for_new_business(session, auth_mock, nr_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    # Create 2 entities - 1 with type NR and another one TMP
    # Affiliate to an org
    # Get should return only 1 - TMP
    # Then delete one affiliation - TMP
    # Get should return only 1 - NR
    patch_token_info(TestJwtClaims.public_account_holder_user, monkeypatch)

    entity_service1 = factory_entity_service(entity_info=TestEntityInfo.name_request)
    entity_dictionary1 = entity_service1.as_dict()
    business_identifier1 = entity_dictionary1['business_identifier']
    name1 = entity_dictionary1['name']

    entity_service2 = factory_entity_service(entity_info=TestEntityInfo.temp_business)
    entity_dictionary2 = entity_service2.as_dict()
    business_identifier2 = entity_dictionary2['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    # create NR affiliation
    affiliation_data = AffiliationData(org_id=org_id, business_identifier=business_identifier1, phone='1112223333')
    AffiliationService.create_new_business_affiliation(affiliation_data)

    # create second row in affiliation table
    AffiliationService.create_affiliation(org_id,
                                          business_identifier2)

    affiliated_entities = AffiliationService.find_visible_affiliations_by_org_id(org_id)

    assert affiliated_entities
    assert len(affiliated_entities) == 1
    assert affiliated_entities[0]['business_identifier'] == business_identifier2
    assert affiliated_entities[0]['nr_number'] == business_identifier1
    assert affiliated_entities[0]['name'] == name1

    delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=business_identifier2)
    AffiliationService.delete_affiliation(delete_affiliation_request)

    affiliated_entities = AffiliationService.find_visible_affiliations_by_org_id(org_id)

    assert affiliated_entities
    assert len(affiliated_entities) == 1
    assert affiliated_entities[0]['business_identifier'] == business_identifier1


def test_find_affiliations_for_new_business_incorporation_complete(session, auth_mock,
                                                                   nr_mock):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be created."""
    # Create 2 entities - 1 with type NR and another one TMP
    # Affiliate to an org
    # Get should return only 1 - TMP
    # Delete NR affiliation
    # Then delete one affiliation - TMP
    # Re-add the TMP affiliation with name as the BC...

    nr_entity = factory_entity_service(entity_info=TestEntityInfo.name_request)
    entity_dictionary1 = nr_entity.as_dict()
    nr_business_identifier = entity_dictionary1['business_identifier']

    tmp_entity = factory_entity_service(entity_info=TestEntityInfo.temp_business)
    entity_dictionary2 = tmp_entity.as_dict()
    tmp_business_identifier = entity_dictionary2['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation_data = AffiliationData(org_id=org_id, business_identifier=nr_business_identifier, phone='1112223333')

    # create NR affiliation
    AffiliationService.create_new_business_affiliation(affiliation_data)

    # create second row in affiliation table
    AffiliationService.create_affiliation(org_id,
                                          tmp_business_identifier)

    affiliated_entities = AffiliationService.find_visible_affiliations_by_org_id(org_id)

    assert affiliated_entities
    assert len(affiliated_entities) == 1
    assert affiliated_entities[0]['business_identifier'] == tmp_business_identifier

    # Delete the NR And TEMP IA affiliation and entities
    delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=tmp_business_identifier)
    AffiliationService.delete_affiliation(delete_affiliation_request)
    tmp_entity.delete()
    delete_affiliation_request.business_identifier = nr_business_identifier
    AffiliationService.delete_affiliation(delete_affiliation_request)
    nr_entity.delete()

    # Create entities for a TEMP with name as BC... number and incorporated entity
    tmp_inc_entity = factory_entity_service(entity_info=TestEntityInfo.temp_business_incoporated)
    entity_dictionary1 = tmp_inc_entity.as_dict()
    tmp_business_incorporated_identifier = entity_dictionary1['business_identifier']
    AffiliationService.create_affiliation(org_id, business_identifier=tmp_business_incorporated_identifier)

    inc_entity = factory_entity_service(entity_info=TestEntityInfo.business_incoporated)
    entity_dictionary1 = inc_entity.as_dict()
    business_incorporated_identifier = entity_dictionary1['business_identifier']
    AffiliationService.create_affiliation(org_id, business_identifier=business_incorporated_identifier)

    affiliated_entities = AffiliationService.find_visible_affiliations_by_org_id(org_id)

    assert affiliated_entities
    assert len(affiliated_entities) == 1
    assert affiliated_entities[0]['business_identifier'] == business_incorporated_identifier


@pytest.mark.parametrize('environment', ['test', None])
def test_fix_stale_affiliations(session, auth_mock, nr_mock, system_user_mock, environment):
    """Assert that an affilation doesn't go stale when transitioning from NR to a business."""
    nr = factory_entity_service(entity_info=TestEntityInfo.name_request).as_dict()

    org_id = factory_org_service().as_dict()['id']
    affiliation1 = AffiliationService.create_affiliation(org_id, business_identifier=nr['business_identifier'],
                                                         environment=environment)

    # Create a new entity with the finalized business identifier. (filer usually does this on registration)
    business = factory_entity_service(entity_info=TestEntityInfo.entity2).as_dict()
    affiliation2 = AffiliationService.create_affiliation(org_id, business_identifier=business['business_identifier'],
                                                         environment=environment)

    assert affiliation1.entity.identifier != affiliation2.entity.identifier

    # Run fix stale affiliations to point the affiliations at the new entity.
    AffiliationService.fix_stale_affiliations(org_id=None, entity_details={
        'identifier': business['business_identifier'],
        'nrNumber': nr['business_identifier'],
        'bootstrapIdentifier': 'gdsf34324'
    }, environment=environment)

    assert affiliation1.entity.identifier == affiliation2.entity.identifier


@pytest.mark.parametrize('environment', ['test', None])
def test_find_affiliation(session, auth_mock, environment):  # pylint:disable=unused-argument
    """Assert that an Affiliation can be retrieve by org id and business identifier."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    # create first row in affiliation table
    AffiliationService.create_affiliation(org_id,
                                          business_identifier,
                                          environment,
                                          TestEntityInfo.entity_lear_mock['passCode'])

    affiliation = AffiliationService.find_affiliation(org_id, business_identifier, environment)

    assert affiliation
    assert affiliation['business']['business_identifier'] == business_identifier
    assert affiliation['organization']['id'] == org_dictionary['id']


def test_create_affiliation_multiple_environments(session, auth_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that same Affiliation can be created in different environments."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation_dev = AffiliationService.create_affiliation(org_id, business_identifier, 'dev',
                                                            TestEntityInfo.entity_lear_mock['passCode'])
    assert affiliation_dev
    assert affiliation_dev.entity.identifier == entity_service.identifier
    assert affiliation_dev.as_dict()['organization']['id'] == org_dictionary['id']

    affiliation_test = AffiliationService.create_affiliation(org_id, business_identifier, 'test',
                                                             TestEntityInfo.entity_lear_mock['passCode'])
    assert affiliation_test
    assert affiliation_test.entity.identifier == entity_service.identifier
    assert affiliation_test.as_dict()['organization']['id'] == org_dictionary['id']

    affiliation_dev = AffiliationService.find_affiliation(org_id, business_identifier, 'dev')
    assert affiliation_dev
    assert affiliation_dev['business']['business_identifier'] == business_identifier
    assert affiliation_dev['organization']['id'] == org_dictionary['id']

    affiliation_test = AffiliationService.find_affiliation(org_id, business_identifier, 'test')
    assert affiliation_test
    assert affiliation_test['business']['business_identifier'] == business_identifier
    assert affiliation_test['organization']['id'] == org_dictionary['id']


@pytest.mark.parametrize('environment', ['test', None])
def test_find_affiliation_multiple_environments(session, auth_mock, monkeypatch,
                                                environment):  # pylint:disable=unused-argument
    """Assert that the affiliation record for the specified environment is returned."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation_dev = AffiliationService.create_affiliation(org_id, business_identifier, environment,
                                                            TestEntityInfo.entity_lear_mock['passCode'])
    assert affiliation_dev
    assert affiliation_dev.entity.identifier == entity_service.identifier
    assert affiliation_dev.as_dict()['organization']['id'] == org_dictionary['id']

    affiliation_dev = AffiliationService.find_affiliation(org_id, business_identifier, environment)
    assert affiliation_dev
    assert affiliation_dev['business']['business_identifier'] == business_identifier
    assert affiliation_dev['organization']['id'] == org_dictionary['id']

    with pytest.raises(BusinessException) as exception:
        AffiliationService.find_affiliation(org_id, business_identifier, 'sandbox')
    assert exception.value.code == Error.DATA_NOT_FOUND.name


@pytest.mark.parametrize('environment', ['test'])
def test_delete_affiliation_multiple_environments(session, auth_mock, monkeypatch,
                                                  environment):  # pylint:disable=unused-argument
    """Verify that the affiliation record for the specified environment gets deleted."""
    entity_service = factory_entity_service(entity_info=TestEntityInfo.entity_lear_mock)
    entity_dictionary = entity_service.as_dict()
    business_identifier = entity_dictionary['business_identifier']

    org_service = factory_org_service()
    org_dictionary = org_service.as_dict()
    org_id = org_dictionary['id']

    affiliation_dev = AffiliationService.create_affiliation(org_id, business_identifier, None,
                                                            TestEntityInfo.entity_lear_mock['passCode'])
    assert affiliation_dev
    assert affiliation_dev.entity.identifier == entity_service.identifier
    assert affiliation_dev.as_dict()['organization']['id'] == org_dictionary['id']

    affiliation_test = AffiliationService.create_affiliation(org_id, business_identifier, environment,
                                                             TestEntityInfo.entity_lear_mock['passCode'])
    assert affiliation_test
    assert affiliation_test.entity.identifier == entity_service.identifier
    assert affiliation_test.as_dict()['organization']['id'] == org_dictionary['id']

    with patch.object(ActivityLogPublisher, 'publish_activity', return_value=None):
        delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id, business_identifier=business_identifier)
        AffiliationService.delete_affiliation(delete_affiliation_request, environment=environment)

    with pytest.raises(BusinessException) as exception:
        AffiliationService.find_affiliation(org_id, business_identifier, environment)
    assert exception.value.code == Error.DATA_NOT_FOUND.name

    affiliation_dev = AffiliationService.find_affiliation(org_id, business_identifier)
    assert affiliation_dev
    assert affiliation_dev['business']['business_identifier'] == business_identifier
    assert affiliation_dev['organization']['id'] == org_dictionary['id']
