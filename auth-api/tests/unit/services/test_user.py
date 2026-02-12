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

"""Tests to verify the User Service.

Test-Suite to ensure that the User Service is working as expected.
"""

import json
from unittest import mock
from unittest.mock import patch

import pytest

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import User as UserModel
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.utils.enums import Status
from tests.conftest import mock_token
from tests.utilities.factory_scenarios import (
    KeycloakScenario,
    TestContactInfo,
    TestEntityInfo,
    TestJwtClaims,
    TestOrgInfo,
    TestUserInfo,
)
from tests.utilities.factory_utils import (
    factory_contact_model,
    factory_entity_model,
    factory_membership_model,
    factory_org_model,
    factory_user_model,
    get_tos_latest_version,
    keycloak_add_user,
    keycloak_get_user_by_username,
    patch_token_info,
)


def test_as_dict(session):  # pylint: disable=unused-argument
    """Assert that a user is rendered correctly as a dictionary."""
    user_model = factory_user_model()
    user = UserService(user_model)

    dictionary = user.as_dict()
    assert dictionary["username"] == dict(TestUserInfo.user1)["username"]


def test_user_save_by_token(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a user can be created by token."""
    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    user = UserService.save_from_jwt_token()
    assert user is not None
    dictionary = user.as_dict()
    assert dictionary["username"] == TestJwtClaims.user_test["preferred_username"]
    assert dictionary["keycloak_guid"] == TestJwtClaims.user_test["sub"]


def test_user_update_by_token(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that an existing user can be updated by token."""
    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    user = UserService.save_from_jwt_token()
    assert user is not None

    # Save again to exercise the update path
    user = UserService.save_from_jwt_token()
    assert user is not None
    dictionary = user.as_dict()
    assert dictionary["username"] == TestJwtClaims.user_test["preferred_username"]
    assert dictionary["keycloak_guid"] == TestJwtClaims.user_test["sub"]


def test_user_save_by_token_no_token(session):  # pylint: disable=unused-argument
    """Assert that a user cannot be created from an empty token."""
    user = UserService.save_from_jwt_token()
    assert user is None


def test_delete_otp_for_user(session, auth_mock, keycloak_mock, monkeypatch):
    """Assert that the otp can be reset."""
    org = factory_org_model(org_info=TestOrgInfo.org_regular_bceid)
    admin_user = factory_user_model()
    factory_membership_model(admin_user.id, org.id)
    admin_claims = TestJwtClaims.get_test_real_user(admin_user.keycloak_guid)

    request = KeycloakScenario.create_user_request()
    keycloak_add_user(request)
    user = keycloak_get_user_by_username(request.user_name)
    user = factory_user_model(TestUserInfo.get_bceid_user_with_kc_guid(user.id))
    factory_membership_model(user.id, org.id)

    patch_token_info(admin_claims, monkeypatch)
    UserService.delete_otp_for_user(user.username, org.id)
    user1 = keycloak_get_user_by_username(request.user_name)
    assert "CONFIGURE_TOTP" in json.loads(user1.value()).get("requiredActions")


def test_user_save_by_token_fail(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a user cannot not be created."""
    with patch.object(UserModel, "create_from_jwt_token", return_value=None):
        patch_token_info(TestJwtClaims.user_test, monkeypatch)
        user = UserService.save_from_jwt_token()
        assert user is None


def test_add_contact_to_user(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a contact can be added to a user."""
    user_with_token = dict(TestUserInfo.user_test)
    user_with_token["keycloak_guid"] = TestJwtClaims.user_test["sub"]
    user_with_token["idp_userid"] = TestJwtClaims.user_test["idp_userid"]
    factory_user_model(user_info=user_with_token)

    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    contact = UserService.add_contact(TestContactInfo.contact1).as_dict()

    assert contact["email"] == TestContactInfo.contact1["email"]
    assert contact["phone"] == TestContactInfo.contact1["phone"]
    assert contact["phone_extension"] == TestContactInfo.contact1["phoneExtension"]


def test_add_contact_user_no_user(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a contact cannot be added to a user that does not exist."""
    with pytest.raises(BusinessException) as exception:
        patch_token_info(TestJwtClaims.user_test, monkeypatch)
        UserService.add_contact(TestContactInfo.contact1)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_add_contact_to_user_already_exists(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a contact cannot be added to a user that already has a contact."""
    user_with_token = dict(TestUserInfo.user_test)
    user_with_token["keycloak_guid"] = TestJwtClaims.user_test["sub"]
    user_with_token["idp_userid"] = TestJwtClaims.user_test["idp_userid"]
    factory_user_model(user_info=user_with_token)

    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    UserService.add_contact(TestContactInfo.contact1)

    with pytest.raises(BusinessException) as exception:
        UserService.add_contact(TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_ALREADY_EXISTS.name


def test_update_contact_for_user(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a contact can be updated for a user."""
    user_with_token = dict(TestUserInfo.user_test)
    user_with_token["keycloak_guid"] = TestJwtClaims.user_test["sub"]
    user_with_token["idp_userid"] = TestJwtClaims.user_test["idp_userid"]
    factory_user_model(user_info=user_with_token)

    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    contact = UserService.add_contact(TestContactInfo.contact1).as_dict()

    assert contact is not None

    updated_contact = UserService.update_contact(TestContactInfo.contact2).as_dict()

    assert updated_contact is not None
    assert updated_contact["email"] == TestContactInfo.contact2["email"]


def test_update_terms_of_use_for_user(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a terms of use can be updated for a user."""
    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    UserService.save_from_jwt_token()

    updated_user = UserService.update_terms_of_use(True, 1)
    dictionary = updated_user.as_dict()
    assert dictionary["user_terms"]["isTermsOfUseAccepted"] is True


def test_terms_of_service_prev_version(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a terms of use can be updated for a user."""
    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    UserService.save_from_jwt_token()

    # update TOS with old version
    updated_user = UserService.update_terms_of_use(True, 1)
    dictionary = updated_user.as_dict()
    assert dictionary["user_terms"]["isTermsOfUseAccepted"] is True

    # accepted version from previous step was old.so comparison should return false
    updated_user = UserService.save_from_jwt_token()
    dictionary = updated_user.as_dict()
    assert dictionary["user_terms"]["isTermsOfUseAccepted"] is False

    # update TOS with latest version
    updated_user = UserService.update_terms_of_use(True, get_tos_latest_version())
    dictionary = updated_user.as_dict()
    assert dictionary["user_terms"]["isTermsOfUseAccepted"] is True

    # accepted version from previous step is latest.so comparison should return true
    updated_user = UserService.save_from_jwt_token()
    dictionary = updated_user.as_dict()
    assert dictionary["user_terms"]["isTermsOfUseAccepted"] is True


def test_update_contact_for_user_no_user(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a contact cannot be updated for a user that does not exist."""
    with pytest.raises(BusinessException) as exception:
        patch_token_info(TestJwtClaims.user_test, monkeypatch)
        UserService.update_contact(TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_update_contact_for_user_no_contact(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a contact cannot be updated for a user with no contact."""
    factory_user_model(user_info=TestUserInfo.user_test)

    with pytest.raises(BusinessException) as exception:
        patch_token_info(TestJwtClaims.user_test, monkeypatch)
        UserService.update_contact(TestContactInfo.contact2)
    assert exception.value.code == Error.DATA_NOT_FOUND.name


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_delete_contact_for_user(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a contact can be deleted for a user."""
    user_with_token = dict(TestUserInfo.user_test)
    user_with_token["keycloak_guid"] = TestJwtClaims.user_test["sub"]
    user_with_token["idp_userid"] = TestJwtClaims.user_test["idp_userid"]
    factory_user_model(user_info=user_with_token)

    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    contact = UserService.add_contact(TestContactInfo.contact1).as_dict()

    assert contact is not None

    deleted_contact = UserService.delete_contact().as_dict()

    assert deleted_contact is not None

    contacts = UserService.get_contacts()
    assert contacts.get("contacts") == []


def test_delete_contact_for_user_no_user(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that deleting a contact for a non-existent user raises the right exception."""
    with pytest.raises(BusinessException) as exception:
        patch_token_info(TestJwtClaims.user_test, monkeypatch)
        UserService.delete_contact()
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_delete_contact_for_user_no_contact(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that deleting a contact for a user with no contact raises the right exception."""
    factory_user_model(user_info=TestUserInfo.user_test)

    with pytest.raises(BusinessException) as exception:
        patch_token_info(TestJwtClaims.user_test, monkeypatch)
        UserService.delete_contact()
    assert exception.value.code == Error.DATA_NOT_FOUND.name


def test_find_users(session):  # pylint: disable=unused-argument
    """Assert that a list of users can be retrieved and searched on."""
    factory_user_model()

    factory_user_model(user_info=TestUserInfo.user2)

    users = UserService.find_users(last_name="User")
    assert users is not None
    assert len(users) == 2


def test_user_find_by_token(session, monkeypatch):  # pylint: disable=unused-argument
    """Assert that a user can be found by token."""
    user_with_token = dict(TestUserInfo.user_test)
    user_with_token["keycloak_guid"] = TestJwtClaims.user_test["sub"]
    user_with_token["idp_userid"] = TestJwtClaims.user_test["idp_userid"]
    factory_user_model(user_info=user_with_token)

    found_user = UserService.find_by_jwt_token()
    assert found_user is None

    # User accepted older version terms and conditions should return False
    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    UserService.update_terms_of_use(True, 1)
    found_user = UserService.find_by_jwt_token()
    assert found_user is not None
    dictionary = found_user.as_dict()
    assert dictionary["username"] == TestJwtClaims.user_test["preferred_username"]
    assert dictionary["keycloak_guid"] == TestJwtClaims.user_test["sub"]
    assert dictionary["user_terms"]["isTermsOfUseAccepted"] is False

    # User accepted latest version terms and conditions should return True
    UserService.update_terms_of_use(True, get_tos_latest_version())
    found_user = UserService.find_by_jwt_token()
    dictionary = found_user.as_dict()
    assert dictionary["user_terms"]["isTermsOfUseAccepted"] is True


def test_user_find_by_username(session):  # pylint: disable=unused-argument
    """Assert that a user can be found by username."""
    user_model = factory_user_model()
    user = UserService(user_model)

    user = UserService.find_by_username(None)
    assert user is None

    user = UserService.find_by_username(TestUserInfo.user1["username"])
    assert user is not None
    dictionary = user.as_dict()
    assert dictionary["username"] == dict(TestUserInfo.user1)["username"]


def test_user_find_by_username_no_model_object(session):  # pylint: disable=unused-argument
    """Assert that the business can't be found with no model."""
    username = dict(TestUserInfo.user_test)["username"]

    user = UserService.find_by_username(username)

    assert user is None


def test_user_find_by_username_missing_username(session):  # pylint: disable=unused-argument
    """Assert that the business can't be found by incorrect username."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    user = UserService(user_model)

    user = UserService.find_by_username("foo")

    assert user is None


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_delete_contact_user_link(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that a contact can not be deleted if contact link exists."""
    user_with_token = dict(TestUserInfo.user_test)
    user_with_token["keycloak_guid"] = TestJwtClaims.public_user_role["sub"]
    user_with_token["idp_userid"] = TestJwtClaims.public_user_role["idp_userid"]
    user_model = factory_user_model(user_info=user_with_token)
    user = UserService(user_model)

    patch_token_info(TestJwtClaims.public_user_role, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user.identifier)
    org_dictionary = org.as_dict()
    org_id = org_dictionary["id"]

    contact = factory_contact_model()

    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.org = org._model  # pylint:disable=protected-access
    contact_link = contact_link.flush()
    contact_link.save()

    deleted_contact = UserService.delete_contact()

    assert deleted_contact is None

    delete_contact_link = ContactLinkModel.find_by_user_id(user.identifier)
    assert not delete_contact_link

    exist_contact_link = ContactLinkModel.find_by_org_id(org_id)
    assert exist_contact_link


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_delete_user(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    user_with_token = dict(TestUserInfo.user_test)
    user_with_token["keycloak_guid"] = TestJwtClaims.user_test["sub"]
    user_with_token["idp_userid"] = TestJwtClaims.user_test["idp_userid"]
    user_model = factory_user_model(user_info=user_with_token)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.save()

    patch_token_info(TestJwtClaims.user_test, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)

    UserService.delete_user()
    updated_user = UserModel.find_by_jwt_token()
    assert len(updated_user.contacts) == 0

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == "INACTIVE"


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_delete_user_where_org_has_affiliations(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link = contact_link.flush()
    contact_link.save()

    patch_token_info(TestJwtClaims.user_test, monkeypatch)
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id).as_dict()
    org_id = org["id"]

    entity = factory_entity_model(entity_info=TestEntityInfo.entity_lear_mock)

    affiliation = AffiliationModel(org_id=org_id, entity_id=entity.id)
    affiliation.save()
    with pytest.raises(BusinessException) as exception:
        UserService.delete_user()
        assert exception.code == Error.DELETE_FAILED_ONLY_OWNER

    updated_user = UserModel.find_by_jwt_token()
    contacts = UserService.get_contacts()
    assert len(contacts) == 1

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == "ACTIVE"


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_delete_user_where_user_is_member_on_org(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    # Create a user and org
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.save()

    patch_token_info(
        TestJwtClaims.get_test_user(user_model.keycloak_guid, idp_userid=user_model.idp_userid), monkeypatch
    )
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)
    org_dictionary = org.as_dict()
    org_id = org_dictionary["id"]

    entity = factory_entity_model(entity_info=TestEntityInfo.entity_lear_mock)
    affiliation = AffiliationModel(org_id=org_id, entity_id=entity.id)
    affiliation.save()

    # Create another user and add membership to the above org
    user_model2 = factory_user_model(user_info=TestUserInfo.user2)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model2
    contact_link.save()

    membership = MembershipModel(
        org_id=org_id, user_id=user_model2.id, membership_type_code="USER", membership_type_status=Status.ACTIVE.value
    )
    membership.save()

    patch_token_info(
        TestJwtClaims.get_test_user(user_model2.keycloak_guid, idp_userid=user_model2.idp_userid), monkeypatch
    )
    UserService.delete_user()

    updated_user = UserModel.find_by_jwt_token()
    assert len(updated_user.contacts) == 0

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == "INACTIVE"


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_delete_user_where_org_has_another_owner(session, auth_mock, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that a user can be deleted."""
    # Create a user and org
    user_model = factory_user_model(user_info=TestUserInfo.user_test)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model
    contact_link.save()

    patch_token_info(
        TestJwtClaims.get_test_user(user_model.keycloak_guid, idp_userid=user_model.idp_userid), monkeypatch
    )
    org = OrgService.create_org(TestOrgInfo.org1, user_id=user_model.id)
    org_dictionary = org.as_dict()
    org_id = org_dictionary["id"]

    entity = factory_entity_model(entity_info=TestEntityInfo.entity_lear_mock)
    affiliation = AffiliationModel(org_id=org_id, entity_id=entity.id)
    affiliation.save()

    # Create another user and add membership to the above org
    user_model2 = factory_user_model(user_info=TestUserInfo.user2)
    contact = factory_contact_model()
    contact_link = ContactLinkModel()
    contact_link.contact = contact
    contact_link.user = user_model2
    contact_link.save()

    membership = MembershipModel(
        org_id=org_id, user_id=user_model2.id, membership_type_code="ADMIN", membership_type_status=Status.ACTIVE.value
    )
    membership.save()
    membership.commit()

    # with pytest.raises(BusinessException) as exception:
    patch_token_info(
        TestJwtClaims.get_test_user(user_model2.keycloak_guid, idp_userid=user_model2.idp_userid), monkeypatch
    )
    UserService.delete_user()

    updated_user = UserModel.find_by_jwt_token()
    assert len(updated_user.contacts) == 0

    user_orgs = MembershipModel.find_orgs_for_user(updated_user.id)
    for org in user_orgs:
        assert org.status_code == "INACTIVE"
