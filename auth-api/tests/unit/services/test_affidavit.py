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
"""Tests for the Affidavit service.

Test suite to ensure that the affidavit service routines are working as expected.
"""
from unittest import mock

from auth_api.models import Task as TaskModel
from auth_api.services import Affidavit as AffidavitService
from auth_api.services import Org as OrgService
from auth_api.services import Task as TaskService
from auth_api.utils.enums import AffidavitStatus, LoginSource, OrgStatus, TaskAction, TaskRelationshipStatus, TaskStatus
from tests.conftest import mock_token
from tests.utilities.factory_scenarios import TestAffidavit, TestJwtClaims, TestOrgInfo, TestUserInfo  # noqa: I005
from tests.utilities.factory_utils import factory_user_model, factory_user_model_with_contact, patch_token_info


def test_create_affidavit(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an Affidavit can be created."""
    user = factory_user_model()
    token_info = TestJwtClaims.get_test_real_user(user.keycloak_guid, idp_userid=user.idp_userid)
    patch_token_info(token_info, monkeypatch)
    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    affidavit = AffidavitService.create_affidavit(affidavit_info=affidavit_info)

    assert affidavit
    assert affidavit.as_dict().get("status_code", None) == AffidavitStatus.PENDING.value


def test_create_affidavit_duplicate(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that duplicate Affidavit cannot be created."""
    user = factory_user_model()
    token_info = TestJwtClaims.get_test_real_user(user.keycloak_guid, idp_userid=user.idp_userid)
    patch_token_info(token_info, monkeypatch)

    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    affidavit = AffidavitService.create_affidavit(affidavit_info=affidavit_info)

    assert affidavit.as_dict().get("status_code", None) == AffidavitStatus.PENDING.value
    new_affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    affidavit2 = AffidavitService.create_affidavit(affidavit_info=new_affidavit_info)
    new_affidavit_info_2 = TestAffidavit.get_test_affidavit_with_contact()
    affidavit3 = AffidavitService.create_affidavit(affidavit_info=new_affidavit_info_2)
    assert affidavit.as_dict().get("status_code", None) == AffidavitStatus.INACTIVE.value
    assert affidavit2.as_dict().get("status_code", None) == AffidavitStatus.INACTIVE.value
    assert affidavit3.as_dict().get("status_code", None) == AffidavitStatus.PENDING.value


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_approve_org(session, keycloak_mock, monkeypatch, gcs_mock):  # pylint:disable=unused-argument
    """Assert that an Affidavit can be approved."""
    user = factory_user_model_with_contact(user_info=TestUserInfo.user_bceid_tester)
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid
    )
    patch_token_info(token_info, monkeypatch)

    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=affidavit_info)
    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()
    assert org_dict["status_code"] == OrgStatus.PENDING_STAFF_REVIEW.value
    task_model = TaskModel.find_by_task_for_account(org_dict["id"], status=TaskStatus.OPEN.value)
    assert task_model.relationship_id == org_dict["id"]
    assert task_model.action == TaskAction.AFFIDAVIT_REVIEW.value
    task_info = {
        "status": TaskStatus.OPEN.value,
        "relationshipStatus": TaskRelationshipStatus.ACTIVE.value,
        "remarks": ["Test Remark"],
    }
    task = TaskService.update_task(TaskService(task_model), task_info)
    task_dict = task.as_dict()
    affidavit = AffidavitService.find_affidavit_by_org_id(task_dict["relationship_id"])
    assert affidavit["status_code"] == AffidavitStatus.APPROVED.value


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_task_creation(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that affidavit reupload creates new task."""
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid
    )
    patch_token_info(token_info, monkeypatch)

    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=affidavit_info)
    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_id = org.as_dict().get("id")
    task_model: TaskModel = TaskModel.find_by_task_for_account(org_id, TaskStatus.OPEN.value)
    assert task_model is not None, "New Open should be generated"
    task_model.status = TaskStatus.HOLD.value  # set current task to hold.Its a staff action
    new_affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=new_affidavit_info)
    assert TaskModel.find_by_id(task_model.id).status == TaskStatus.CLOSED.value
    assert TaskModel.find_by_task_for_account(org_id, TaskStatus.OPEN.value) is not None


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_reject_org(session, keycloak_mock, monkeypatch, gcs_mock):
    """Assert that an Affidavit can be rejected."""
    # Setup mock for GCS
    gcs_mock["mock_blob"].generate_signed_url.return_value = "http://mocked.url/document.pdf"

    # Create test user
    user = factory_user_model_with_contact(user_info=TestUserInfo.user_bceid_tester)
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid
    )
    patch_token_info(token_info, monkeypatch)

    # Create test affidavits with proper contact information
    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    # Ensure contact information exists
    assert "contact" in affidavit_info, "Test affidavit data must include contact information"

    affidavit1 = AffidavitService.create_affidavit(affidavit_info=affidavit_info.copy())
    affidavit = AffidavitService.create_affidavit(affidavit_info=affidavit_info.copy())

    # Verify initial status
    assert affidavit1.as_dict().get("status_code") == AffidavitStatus.INACTIVE.value
    assert affidavit.as_dict().get("status_code") == AffidavitStatus.PENDING.value

    # Create org
    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()
    assert org_dict["status_code"] == OrgStatus.PENDING_STAFF_REVIEW.value

    # Find and update task
    task_model = TaskModel.find_by_task_for_account(org_dict["id"], status=TaskStatus.OPEN.value)
    assert task_model.relationship_id == org_dict["id"]
    assert task_model.action == TaskAction.AFFIDAVIT_REVIEW.value

    # Update task to rejected status
    task_info = {
        "status": TaskStatus.OPEN.value,
        "relationshipStatus": TaskRelationshipStatus.REJECTED.value,
        "remarks": ["Test Remark"],
    }
    task = TaskService.update_task(TaskService(task_model), task_info)
    task_dict = task.as_dict()

    # Verify affidavit was rejected
    affidavit = AffidavitService.find_affidavit_by_org_id(task_dict["relationship_id"])
    assert affidavit["status_code"] == AffidavitStatus.REJECTED.value

    # Verify GCS mock was called
    assert gcs_mock["mock_blob"].generate_signed_url.called


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_reject_org_with_inactive_affidavit(session, keycloak_mock, monkeypatch, gcs_mock):
    """Assert that an org can be rejected when affidavit is INACTIVE (Scenario 1)."""
    # Setup mock for GCS
    gcs_mock["mock_blob"].generate_signed_url.return_value = "http://mocked.url/document.pdf"

    # Create test user
    user = factory_user_model_with_contact(user_info=TestUserInfo.user_bceid_tester)
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid
    )
    patch_token_info(token_info, monkeypatch)

    # Create test affidavit and org
    affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    affidavit = AffidavitService.create_affidavit(affidavit_info=affidavit_info)
    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()

    # Find the task and set it to HOLD (simulating staff action)
    task_model = TaskModel.find_by_task_for_account(org_dict["id"], status=TaskStatus.OPEN.value)
    task_model.status = TaskStatus.HOLD.value
    task_model.save()

    # Create another affidavit which will make the first one INACTIVE
    new_affidavit_info = TestAffidavit.get_test_affidavit_with_contact()
    AffidavitService.create_affidavit(affidavit_info=new_affidavit_info)

    # Verify first affidavit is now INACTIVE
    affidavit1 = AffidavitService.find_affidavit_by_org_id(org_dict["id"])
    assert affidavit1["status_code"] == AffidavitStatus.PENDING.value  # The new one

    # Find the new task that was created
    task_model = TaskModel.find_by_task_for_account(org_dict["id"], status=TaskStatus.OPEN.value)

    # Now try to reject the org - this should work even with INACTIVE affidavit
    task_info = {
        "status": TaskStatus.OPEN.value,
        "relationshipStatus": TaskRelationshipStatus.REJECTED.value,
        "remarks": ["Rejecting with inactive affidavit"],
    }
    task = TaskService.update_task(TaskService(task_model), task_info)

    # Verify org was rejected
    org = OrgService.find_by_org_id(org_dict["id"])
    assert org.as_dict()["status_code"] == OrgStatus.REJECTED.value


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_reject_org_without_affidavit(session, keycloak_mock, monkeypatch):
    """Assert that an org can be rejected when no affidavit exists (Scenario 2)."""
    # Create test user (staff)
    staff_user = factory_user_model_with_contact(user_info=TestUserInfo.user_staff_admin)
    staff_token_info = TestJwtClaims.get_test_user(
        sub=staff_user.keycloak_guid,
        source=LoginSource.STAFF.value,
        idp_userid=staff_user.idp_userid,
        roles=["staff", "create_accounts"],
    )

    # First create an org as a regular user without affidavit
    user = factory_user_model_with_contact(user_info=TestUserInfo.user_bceid_tester)
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid
    )
    patch_token_info(token_info, monkeypatch)

    # Create org without creating an affidavit first
    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()

    # Switch to staff user for rejection
    patch_token_info(staff_token_info, monkeypatch)

    # Find the task
    task_model = TaskModel.find_by_task_for_account(org_dict["id"], status=TaskStatus.OPEN.value)

    # Try to reject the org - this should work even without affidavit
    task_info = {
        "status": TaskStatus.OPEN.value,
        "relationshipStatus": TaskRelationshipStatus.REJECTED.value,
        "remarks": ["Rejecting without affidavit"],
    }
    task = TaskService.update_task(TaskService(task_model), task_info)

    # Verify org was rejected
    org = OrgService.find_by_org_id(org_dict["id"])
    assert org.as_dict()["status_code"] == OrgStatus.REJECTED.value
