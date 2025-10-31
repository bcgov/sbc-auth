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
from auth_api.services import User as UserService
from auth_api.utils.enums import (
    AffidavitStatus,
    LoginSource,
    OrgStatus,
    TaskAction,
    TaskRelationshipStatus,
    TaskRelationshipType,
    TaskStatus,
    TaskTypePrefix,
)
from tests.conftest import mock_token
from tests.utilities.factory_scenarios import TestAffidavit, TestJwtClaims, TestOrgInfo, TestUserInfo  # noqa: I001
from tests.utilities.factory_utils import (
    factory_membership_model,
    factory_org_model,
    factory_task_model,
    factory_user_model,
    factory_user_model_with_contact,
    patch_token_info,
)


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
@mock.patch("auth_api.services.org.Org.send_staff_review_account_reminder")
def test_modify_task_multiple_orgs_multiple_tasks(mock_send_reminder, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that _modify_task handles multiple orgs with multiple tasks correctly."""
    user = factory_user_model_with_contact()
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid
    )
    patch_token_info(token_info, monkeypatch)

    org1 = factory_org_model(TestOrgInfo.org1, user_id=user.id)
    org2 = factory_org_model(TestOrgInfo.org1, user_id=user.id)
    org3 = factory_org_model(TestOrgInfo.org1, user_id=user.id)

    factory_membership_model(user_id=user.id, org_id=org1.id)
    factory_membership_model(user_id=user.id, org_id=org2.id)
    factory_membership_model(user_id=user.id, org_id=org3.id)

    task1 = factory_task_model(
        user_id=user.id,
        org_id=org1.id,
    )
    task1.status = TaskStatus.HOLD.value
    task1.relationship_type = TaskRelationshipType.ORG.value
    task1.action = TaskAction.ACCOUNT_REVIEW.value
    task1.type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    task1.account_id = org1.id
    task1.save()

    task2 = factory_task_model(
        user_id=user.id,
        org_id=org2.id,
    )
    task2.status = TaskStatus.HOLD.value
    task2.relationship_type = TaskRelationshipType.USER.value
    task2.relationship_id = user.id
    task2.action = TaskAction.AFFIDAVIT_REVIEW.value
    task2.type = TaskTypePrefix.BCEID_ADMIN.value
    task2.account_id = org2.id
    task2.save()

    task3 = factory_task_model(
        user_id=user.id,
        org_id=org3.id,
    )
    task3.status = TaskStatus.HOLD.value
    task3.relationship_type = TaskRelationshipType.ORG.value
    task3.action = TaskAction.AFFIDAVIT_REVIEW.value
    task3.type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
    task3.account_id = org3.id
    task3.save()

    user_service = UserService(user)
    AffidavitService._modify_task(user_service)  # pylint: disable=protected-access

    assert TaskModel.find_by_id(task1.id).status == TaskStatus.CLOSED.value
    assert TaskModel.find_by_id(task2.id).status == TaskStatus.CLOSED.value
    assert TaskModel.find_by_id(task3.id).status == TaskStatus.CLOSED.value

    new_task1 = TaskModel.find_by_task_for_account(org1.id, TaskStatus.OPEN.value)
    assert new_task1 is not None
    assert new_task1.status == TaskStatus.OPEN.value
    assert new_task1.relationship_id == org1.id

    new_task2 = TaskModel.find_by_user_and_status(org2.id, TaskStatus.OPEN.value)
    assert new_task2 is not None
    assert new_task2.status == TaskStatus.OPEN.value
    assert new_task2.account_id == org2.id

    new_task3 = TaskModel.find_by_task_for_account(org3.id, TaskStatus.OPEN.value)
    assert new_task3 is not None
    assert new_task3.status == TaskStatus.OPEN.value
    assert new_task3.relationship_id == org3.id

    assert mock_send_reminder.call_count >= 3


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_approve_or_reject_no_affidavit_allows_rejection(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that approve_or_reject allows rejection even when no affidavit exists."""
    user = factory_user_model_with_contact()
    reviewer_user = factory_user_model_with_contact(user_info=TestUserInfo.user_bceid_tester)
    token_info = TestJwtClaims.get_test_user(
        sub=user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=user.idp_userid
    )
    patch_token_info(token_info, monkeypatch)

    org = OrgService.create_org(TestOrgInfo.org_with_mailing_address(), user_id=user.id)
    org_dict = org.as_dict()

    result = AffidavitService.approve_or_reject(org_id=org_dict["id"], is_approved=False, user=reviewer_user)

    assert result is None


@mock.patch("auth_api.services.affiliation_invitation.RestService.get_service_account_token", mock_token)
def test_approve_or_reject_bceid_admin_no_affidavit_allows_rejection(session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that approve_or_reject_bceid_admin allows rejection even when no affidavit exists."""
    admin_user = factory_user_model_with_contact()
    reviewer_user = factory_user_model_with_contact(user_info=TestUserInfo.user_bceid_tester)
    token_info = TestJwtClaims.get_test_user(
        sub=admin_user.keycloak_guid, source=LoginSource.BCEID.value, idp_userid=admin_user.idp_userid
    )
    patch_token_info(token_info, monkeypatch)

    result = AffidavitService.approve_or_reject_bceid_admin(
        admin_user_id=admin_user.id, is_approved=False, user=reviewer_user
    )

    assert result is None
