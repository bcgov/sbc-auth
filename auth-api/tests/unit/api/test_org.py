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

import json
import uuid
from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import patch

import pytest
import pytz
from faker import Faker

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Affidavit as AffidavitModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models.dataclass import TaskSearch
from auth_api.schemas import utils as schema_utils
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Invitation as InvitationService
from auth_api.services import Org as OrgService
from auth_api.services import Task as TaskService
from auth_api.services import User as UserService
from auth_api.utils.enums import (
    AccessType,
    AffidavitStatus,
    CorpType,
    LoginSource,
    NRActionCodes,
    NRStatus,
    OrgStatus,
    OrgType,
    PatchActions,
    PaymentMethod,
    ProductCode,
    ProductSubscriptionStatus,
    SuspensionReasonCode,
    TaskAction,
    TaskRelationshipStatus,
    TaskRelationshipType,
    TaskStatus,
)
from auth_api.utils.roles import ADMIN  # noqa: I001
from tests.utilities.factory_scenarios import (
    DeleteAffiliationPayload,
    TestAffidavit,
    TestAffliationInfo,
    TestContactInfo,
    TestEntityInfo,
    TestJwtClaims,
    TestOrgInfo,
    TestPaymentMethodInfo,
    TestUserInfo,
)
from tests.utilities.factory_utils import (
    convert_org_to_staff_org,
    factory_auth_header,
    factory_invitation,
    factory_membership_model,
    factory_org_model,
    factory_user_model,
    patch_pay_account_delete,
    patch_pay_account_delete_error,
    patch_pay_account_fees,
    patch_pay_account_post,
)

FAKE = Faker()


@pytest.mark.parametrize(
    "org_info",
    [
        TestOrgInfo.org1,
        TestOrgInfo.org_onlinebanking,
        TestOrgInfo.org_with_products,
        TestOrgInfo.org_regular,
        TestOrgInfo.org_with_all_info,
    ],
)
def test_add_org(client, jwt, session, keycloak_mock, org_info):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post("/api/v1/orgs", data=json.dumps(org_info), headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.CREATED
    assert schema_utils.validate(rv.json, "org_response")[0]


@pytest.mark.parametrize(
    "has_contact, expected_status_code", [("with_contact", HTTPStatus.CREATED), ("no_contact", HTTPStatus.CREATED)]
)
def test_add_org_v2_with_contact(client, jwt, session, keycloak_mock, has_contact, expected_status_code):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed with contact using v2 endpoint."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")

    org_data = TestOrgInfo.org1.copy()

    if has_contact == "with_contact":
        org_data["contact"] = TestContactInfo.contact1

    rv = client.post("/api/v2/orgs", data=json.dumps(org_data), headers=headers, content_type="application/json")
    assert rv.status_code == expected_status_code
    dictionary = json.loads(rv.data)
    assert dictionary["name"] == TestOrgInfo.org1["name"]
    if has_contact == "with_contact":
        assert "contact" in dictionary
        assert dictionary["contact"]["email"] == TestContactInfo.contact1["email"]
        assert dictionary["contact"]["phone"] == TestContactInfo.contact1["phone"]
    else:
        assert "contact" not in dictionary  # Ensure no contact is present in the response
    assert schema_utils.validate(rv.json, "org_response")[0]


def test_add_org_v2_with_contact_fields_too_long(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org with contact fields exceeding maxLength returns 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")

    org_data = TestOrgInfo.org1.copy()
    org_data["contact"] = {
        "email": "a" * 101,
        "phone": "1" * 16,
        "phoneExtension": "1" * 11,
        "street": "a" * 251,
        "streetAdditional": "a" * 251,
        "city": "a" * 101,
        "region": "a" * 101,
        "country": "a" * 21,
        "postalCode": "a" * 16,
        "deliveryInstructions": "a" * 4097,
    }

    rv = client.post("/api/v2/orgs", data=json.dumps(org_data), headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.BAD_REQUEST
    assert "message" in rv.json


def test_add_basic_org_with_pad_throws_error(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    org_info = {"name": "My Test Org", "paymentType": "PAD"}
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post("/api/v1/orgs", data=json.dumps(org_info), headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_org_by_client(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be searched."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED

    # Ensure no exception is thrown by including letters in the id.
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.get("/api/v1/orgs?id={}".format("FFF1234"), headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK

    # system search
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.get(
        "/api/v1/orgs?name={}".format(TestOrgInfo.org1.get("name")), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.OK
    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("name") == TestOrgInfo.org1.get("name")

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.get(
        "/api/v1/orgs?name={}".format(TestOrgInfo.org1.get("name")), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.OK
    orgs = json.loads(rv.data)
    assert bool(orgs) is False

    rv = client.get(
        "/api/v1/orgs?name={}".format("notanexistingorgname"), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.NO_CONTENT

    # staff search
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get(
        "/api/v1/orgs?name={}".format(TestOrgInfo.org1.get("name")), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("name") == TestOrgInfo.org1.get("name")

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get("/api/v1/orgs?status={}".format("ACTIVE"), headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("name") == TestOrgInfo.org1.get("name")

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get(
        "/api/v1/orgs?status={}&type={}".format("ACTIVE", "REGULAR"), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("name") == TestOrgInfo.org1.get("name")


def test_duplicate_name(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be searched using multiple syntax."""
    # Create active org
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    name = TestOrgInfo.org1.get("name")
    rv = client.get(f"/api/v1/orgs?validateName=true&name={name}", headers=headers, content_type="application/json")

    assert rv.status_code == HTTPStatus.OK

    # not existing brnach name ; so 204
    rv = client.get(
        f"/api/v1/orgs?validateName=true&name={name}&branchName=foo", headers=headers, content_type="application/json"
    )

    assert rv.status_code == HTTPStatus.NO_CONTENT

    # empty brnach name; so 200
    rv = client.get(
        f"/api/v1/orgs?validateName=true&name={name}&branchName=", headers=headers, content_type="application/json"
    )

    assert rv.status_code == HTTPStatus.OK

    # does not conflict with rejected accounts
    rejected_org = factory_org_model(org_info=TestOrgInfo.org2)
    rejected_org.status_code = OrgStatus.REJECTED.value
    rejected_org.save()

    rv = client.get(
        f"/api/v1/orgs?validateName=true&name={rejected_org.name}&branchName=",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.NO_CONTENT


def test_search_org_by_client_multiple_status(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be searched using multiple syntax."""
    # Create active org
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    document_signature = client.get(
        "/api/v1/documents/test.jpeg/signatures", headers=headers, content_type="application/json"
    )
    doc_key = document_signature.json.get("key")
    client.post(
        "/api/v1/users/{}/affidavits".format(TestJwtClaims.public_user_role.get("sub")),
        headers=headers,
        data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
        content_type="application/json",
    )

    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address(name="foobar1")),
        headers=headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED

    # create suspended org
    public_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post("/api/v1/users", headers=public_headers, content_type="application/json")

    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=public_headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps(
            {"statusCode": OrgStatus.SUSPENDED.value, "suspensionReasonCode": SuspensionReasonCode.OWNER_CHANGE.name}
        ),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.json.get("orgStatus") == OrgStatus.SUSPENDED.value

    # staff search
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get("/api/v1/orgs", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 3

    rv = client.get("/api/v1/orgs?status=ACTIVE&status=SUSPENDED", headers=headers, content_type="application/json")

    orgs = json.loads(rv.data)
    assert orgs.get("total") == 2

    rv = client.get(
        "/api/v1/orgs?status=ACTIVE&status=SUSPENDED&status=PENDING_STAFF_REVIEW",
        headers=headers,
        content_type="application/json",
    )

    orgs = json.loads(rv.data)
    assert orgs.get("total") == 3

    rv = client.get(
        "/api/v1/orgs?status=ACTIVE&status=SUSPENDED&status=PENDING_STAFF_REVIEW&status=ABCS",
        headers=headers,
        content_type="application/json",
    )

    orgs = json.loads(rv.data)
    assert orgs.get("total") == 3

    rv = client.get("/api/v1/orgs?status=PENDING_STAFF_REVIEW", headers=headers, content_type="application/json")

    orgs = json.loads(rv.data)
    assert orgs.get("total") == 1


def test_search_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be searched."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)

    # staff search with manage account role gets 1 org
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get("/api/v1/orgs", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert len(orgs.get("orgs")) == 1

    # staff search with staff_admin_role gets 1 org
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.get("/api/v1/orgs", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert len(orgs.get("orgs")) == 1

    # staff search with out manage account role gets only normal org
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_view_accounts_role)
    rv = client.get("/api/v1/orgs", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert len(orgs.get("orgs")) == 1


def test_add_govm_org_staff_admin(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org_govm), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    dictionary = json.loads(rv.data)
    assert dictionary["accessType"] == AccessType.GOVM.value
    assert dictionary["orgType"] == OrgType.PREMIUM.value
    assert dictionary["orgStatus"] == OrgStatus.PENDING_INVITE_ACCEPT.value
    assert schema_utils.validate(rv.json, "org_response")[0]


def test_add_govm_full_flow(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org_govm), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    assert dictionary.get("branchName") == TestOrgInfo.org_govm.get("branchName")
    org_id = dictionary["id"]
    # Invite a user to the org
    rv = client.post(
        "/api/v1/invitations",
        data=json.dumps(factory_invitation(org_id, "abc123@email.com", membership_type=ADMIN)),
        headers=headers,
        content_type="application/json",
    )
    dictionary = json.loads(rv.data)
    invitation_id = dictionary["id"]
    invitation_id_token = InvitationService.generate_confirmation_token(invitation_id)

    # Get pending members for the org as invitee and assert length of 1
    rv = client.get(f"/api/v1/orgs/{org_id}/members?status=ACTIVE", headers=headers)
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)

    # Create/login as invited user
    headers_invited = factory_auth_header(jwt=jwt, claims=TestJwtClaims.gov_account_holder_user)
    rv = client.post("/api/v1/users", headers=headers_invited, content_type="application/json")

    # Accept invite as invited user
    rv = client.put(
        f"/api/v1/invitations/tokens/{invitation_id_token}",
        headers=headers_invited,
        content_type="application/json",
    )

    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert dictionary["status"] == "ACCEPTED"

    # Get ACTIVE members for the org as invitee and assert length of 1
    rv = client.get(f"/api/v1/orgs/{org_id}/members?status=ACTIVE", headers=headers)
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert dictionary["members"]
    assert len(dictionary["members"]) == 1

    update_org_payload = {
        "mailingAddress": {
            "city": "Innisfail",
            "country": "CA",
            "region": "AB",
            "postalCode": "T4G 1P5",
            "street": "D-4619 45 Ave",
            "streetAdditional": "",
        },
        "paymentInfo": {
            "revenueAccount": {"projectCode": "100", "responsibilityCentre": "100", "serviceLine": "100", "stob": "100"}
        },
        "productSubscriptions": [{"productCode": "VS"}, {"productCode": "BCA"}],
    }
    rv = client.put(
        f"/api/v1/orgs/{org_id}",
        data=json.dumps(update_org_payload),
        headers=headers_invited,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK

    rv_products = client.get(
        f"/api/v1/orgs/{org_id}/products", headers=headers_invited, content_type="application/json"
    )
    list_products = json.loads(rv_products.data)

    vs_product = next(x for x in list_products if x.get("code") == "VS")
    assert vs_product.get("subscriptionStatus") == "PENDING_STAFF_REVIEW"


def test_add_govm_org_by_user_exception(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org_govm), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_add_org_staff_admin_any_number_of_orgs(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org2), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org3), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org4), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org5), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED


def test_add_org_multiple(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed.But in limited number."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv1 = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv1.status_code == HTTPStatus.CREATED
    rv2 = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org2), headers=headers, content_type="application/json"
    )
    assert rv2.status_code == HTTPStatus.CREATED
    rv3 = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org3), headers=headers, content_type="application/json"
    )
    assert rv3.status_code == HTTPStatus.CREATED
    rv4 = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org4), headers=headers, content_type="application/json"
    )

    # max number of orgs reached.
    assert rv4.status_code == HTTPStatus.BAD_REQUEST


def test_add_same_org_409(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED, "created first org"
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CONFLICT, "not able to create duplicates org"


def test_create_govn_org_with_products_single_staff_review_task(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Ensure GOVN org creation creates only a staff review task.

    Verify task status updates correctly when a product is re-added
    after approval.
    """
    patch_pay_account_post(monkeypatch)
    patch_pay_account_fees(monkeypatch, [ProductCode.BUSINESS_SEARCH.value, ProductCode.PPR.value])

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")

    govn_org_payload = {
        "name": "test govn single task",
        "accessType": AccessType.GOVN.value,
        "typeCode": OrgType.PREMIUM.value,
        "productSubscriptions": [
            {"productCode": ProductCode.BUSINESS_SEARCH.value},
            {"productCode": ProductCode.PPR.value},
        ],
        "mailingAddress": TestOrgInfo.get_mailing_address(),
        "paymentInfo": {"paymentMethod": PaymentMethod.DIRECT_PAY.value},
    }

    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(govn_org_payload),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED
    org_id = rv.json["id"]

    task_search = TaskSearch(status=[TaskStatus.OPEN.value], page=1, limit=100)
    tasks_result = TaskService.fetch_tasks(task_search)
    tasks = tasks_result["tasks"]

    org_tasks = [
        t
        for t in tasks
        if t.get("account_id") == org_id
        or (t.get("relationship_type") == TaskRelationshipType.ORG.value and t.get("relationship_id") == org_id)
    ]
    assert len(org_tasks) == 1, "expected exactly one staff review task for the new org"
    single_task = org_tasks[0]
    assert single_task["relationship_type"] == TaskRelationshipType.ORG.value
    assert single_task["action"] == TaskAction.ACCOUNT_REVIEW.value

    product_tasks = [t for t in tasks if t.get("relationship_type") == TaskRelationshipType.PRODUCT.value]
    assert not any(t.get("account_id") == org_id for t in product_tasks), (
        "expected no NEW_PRODUCT_FEE_REVIEW / product task for GOVN org creation"
    )

    # Approve org task, remove product, re-add
    staff_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv_approve = client.put(
        f"/api/v1/tasks/{single_task['id']}",
        data=json.dumps({
            "status": TaskStatus.COMPLETED.value,
            "relationshipStatus": TaskRelationshipStatus.ACTIVE.value,
        }),
        headers=staff_headers,
        content_type="application/json",
    )
    assert rv_approve.status_code == HTTPStatus.OK

    product_code = ProductCode.BUSINESS_SEARCH.value
    rv_delete = client.delete(
        f"/api/v1/orgs/{org_id}/products/{product_code}",
        headers=headers,
        content_type="application/json",
    )
    assert rv_delete.status_code == HTTPStatus.OK

    rv_products = client.post(
        f"/api/v1/orgs/{org_id}/products",
        data=json.dumps({"subscriptions": [{"productCode": product_code}]}),
        headers=headers,
        content_type="application/json",
    )
    assert rv_products.status_code == HTTPStatus.CREATED
    subscriptions = rv_products.json.get("subscriptions", [])
    product = next((p for p in subscriptions if p.get("code") == product_code), None)
    assert product is not None
    assert product["subscriptionStatus"] == ProductSubscriptionStatus.ACTIVE.value


def test_govn_org_add_product_pending_staff_review(
    client, jwt, session, keycloak_mock, monkeypatch
):  # pylint:disable=unused-argument
    """Assert adding a product to a GOVN org via POST /orgs/{id}/products results in PENDING_STAFF_REVIEW."""
    patch_pay_account_post(monkeypatch)
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")

    govn_org_payload = {
        "name": "test govn add product",
        "accessType": AccessType.GOVN.value,
        "typeCode": OrgType.PREMIUM.value,
        "mailingAddress": TestOrgInfo.get_mailing_address(),
        "paymentInfo": {"paymentMethod": PaymentMethod.DIRECT_PAY.value},
    }
    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(govn_org_payload),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED
    org_id = rv.json["id"]

    product_code = ProductCode.BUSINESS_SEARCH.value
    rv_products = client.post(
        f"/api/v1/orgs/{org_id}/products",
        data=json.dumps({"subscriptions": [{"productCode": product_code}]}),
        headers=headers,
        content_type="application/json",
    )
    assert rv_products.status_code == HTTPStatus.CREATED
    subscriptions = rv_products.json.get("subscriptions", [])
    product = next((p for p in subscriptions if p.get("code") == product_code), None)
    assert product is not None, f"Product {product_code} should appear in response"
    assert product["subscriptionStatus"] == ProductSubscriptionStatus.PENDING_STAFF_REVIEW.value, (
        "GOVN org adding product should require staff review"
    )


@pytest.mark.parametrize(
    "product_code,expected_status,use_factory_org,claims_attr,assert_no_product_task",
    [
        (ProductCode.NDS.value, ProductSubscriptionStatus.ACTIVE.value, True, "system_role", True),
        (ProductCode.VS.value, ProductSubscriptionStatus.PENDING_STAFF_REVIEW.value, False, "public_user_role", False),
    ],
)
def test_post_org_products_skip_auth_system_vs_org_admin(
    client, jwt, session, keycloak_mock, monkeypatch,
    product_code, expected_status, use_factory_org, claims_attr, assert_no_product_task,
):  # pylint:disable=unused-argument
    """Assert POST /orgs/{id}/products: SYSTEM vs org admin (non-GOVN/GOVM); focus on PENDING_STAFF_REVIEW for org admin."""
    headers = factory_auth_header(jwt=jwt, claims=getattr(TestJwtClaims, claims_attr))

    if use_factory_org:
        regular_org = factory_org_model(org_info={"name": "regular org for system", "accessType": AccessType.REGULAR.value})
        org_id = regular_org.id
    else:
        patch_pay_account_post(monkeypatch)
        client.post("/api/v1/users", headers=headers, content_type="application/json")
        rv = client.post(
            "/api/v1/orgs",
            data=json.dumps({
                "name": "regular org for org admin",
                "accessType": AccessType.REGULAR.value,
                "typeCode": OrgType.PREMIUM.value,
                "mailingAddress": TestOrgInfo.get_mailing_address(),
                "paymentInfo": {"paymentMethod": PaymentMethod.DIRECT_PAY.value},
            }),
            headers=headers,
            content_type="application/json",
        )
        assert rv.status_code == HTTPStatus.CREATED
        org_id = rv.json["id"]

    rv_products = client.post(
        f"/api/v1/orgs/{org_id}/products",
        data=json.dumps({"subscriptions": [{"productCode": product_code}]}),
        headers=headers,
        content_type="application/json",
    )
    assert rv_products.status_code == HTTPStatus.CREATED
    subs = rv_products.json.get("subscriptions", [])
    product = next((p for p in subs if p.get("code") == product_code), None)
    if assert_no_product_task:
        # NDS is hidden: POST response may not include it; use GET ?include_hidden=true to verify (as in prod workflow)
        get_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_view_accounts_role)
        rv_get = client.get(
            f"/api/v1/orgs/{org_id}/products?include_hidden=true",
            headers=get_headers,
        )
        assert rv_get.status_code == HTTPStatus.OK
        subs = json.loads(rv_get.data)
        product = next((p for p in subs if p.get("code") == product_code), None)
    assert product is not None
    assert product["subscriptionStatus"] == expected_status

    if assert_no_product_task:
        product_tasks = [
            t for t in TaskService.fetch_tasks(TaskSearch(status=[TaskStatus.OPEN.value], page=1, limit=100))["tasks"]
            if t.get("relationship_type") == TaskRelationshipType.PRODUCT.value and t.get("account_id") == org_id
        ]
        assert len(product_tasks) == 0, "SYSTEM adding product should not create a product review task"


def test_add_org_invalid_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.invalid), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_org_invalid_space_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.invalid_name_space),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_org_invalid_spaces_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.invalid_name_spaces),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_org_invalid_end_space_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.invalid_name_end_space),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_org_invalid_start_space_returns_400(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 400."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.invalid_name_start_space),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_org_invalid_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 401."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.view_role)
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_add_org_normal_staff_invalid_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns a 401."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.staff_role)
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_add_org_invalid_user_returns_401(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an org with invalid user returns a 401."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)

    with patch.object(UserService, "find_by_jwt_token", return_value=None):
        rv = client.post(
            "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
        )
        assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_add_org_invalid_returns_exception(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that POSTing an invalid org returns an exception."""
    headers = factory_auth_header(jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")

    with patch.object(OrgService, "create_org", side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)):
        rv = client.post(
            "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
        )
        assert rv.status_code == 400
        assert schema_utils.validate(rv.json, "exception")[0]


def test_get_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved via GET."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "org_response")[0]
    dictionary = json.loads(rv.data)
    assert dictionary["id"] == org_id


def test_get_org_no_auth_returns_401(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org cannot be retrieved without an authorization header."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]
    rv = client.get(f"/api/v1/orgs/{org_id}", headers=None, content_type="application/json")
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_get_org_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that attempting to retrieve a non-existent org returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    rv = client.get(f"/api/v1/orgs/{999}", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_update_org_duplicate_branch_name(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    # assert updating branch name works
    new_branch_name = FAKE.name()
    rv = client.put(
        f"/api/v1/orgs/{org_id}",
        data=json.dumps({"branchName": new_branch_name}),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    dictionary = json.loads(rv.data)
    assert dictionary.get("branchName") == new_branch_name
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    new_org_id = dictionary["id"]

    # assert updating branch name to same name doesnt work
    rv = client.put(
        f"/api/v1/orgs/{new_org_id}",
        data=json.dumps({"branchName": new_branch_name}),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CONFLICT


def test_update_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    # get created org and assert there is no contacts
    rv = client.get(f"/api/v1/orgs/{org_id}/contacts", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    # assert no contacts
    assert len(dictionary.get("contacts")) == 0

    # assert updating org name works alrite
    name = FAKE.name()
    rv = client.put(
        f"/api/v1/orgs/{org_id}",
        data=json.dumps({"name": name}),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    dictionary = json.loads(rv.data)
    assert dictionary.get("name") == name

    # update mailing address
    org_with_mailing_address = TestOrgInfo.update_org_with_mailing_address()
    rv = client.put(
        f"/api/v1/orgs/{org_id}",
        data=json.dumps(org_with_mailing_address),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK

    rv = client.get(f"/api/v1/orgs/{org_id}/contacts", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK

    assert schema_utils.validate(rv.json, "contacts")[0]

    dictionary = json.loads(rv.data)
    actual_mailing_address = org_with_mailing_address.get("mailingAddress")
    assert actual_mailing_address.get("city") == dictionary["contacts"][0].get("city")
    assert actual_mailing_address.get("postalCode") == dictionary["contacts"][0].get("postalCode")

    # Update other org details
    all_org_info = TestOrgInfo.update_org_with_all_info
    rv = client.put(
        f"/api/v1/orgs/{org_id}", data=json.dumps(all_org_info), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.OK
    assert rv.json.get("businessType") == all_org_info["businessType"]
    assert rv.json.get("businessSize") == all_org_info["businessSize"]
    assert rv.json.get("isBusinessAccount") == all_org_info["isBusinessAccount"]


def test_update_org_payment_method_for_org(client, jwt, session, keycloak_mock):
    """Assert that an orgs payment details can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    new_payment_method = TestPaymentMethodInfo.get_payment_method_input(PaymentMethod.ONLINE_BANKING)
    rv = client.put(
        f"/api/v1/orgs/{org_id}", data=json.dumps(new_payment_method), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.OK

    new_payment_method = {"paymentInfo": {"paymentMethod": PaymentMethod.BCOL.value}}
    rv = client.put(
        f"/api/v1/orgs/{org_id}", data=json.dumps(new_payment_method), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.OK


def test_update_premium_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.bcol_linked()), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json.get("orgType") == OrgType.PREMIUM.value
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]
    # Update with same data
    rv = client.put(
        f"/api/v1/orgs/{org_id}",
        data=json.dumps(TestOrgInfo.update_bcol_linked()),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "org_response")[0]


def test_update_org_type_to_staff_fails(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that org type doesn't get updated."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.bcol_linked()), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json.get("orgType") == OrgType.PREMIUM.value
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    data = TestOrgInfo.update_bcol_linked()
    data["typeCode"] = OrgType.SBC_STAFF.value

    rv = client.put(f"/api/v1/orgs/{org_id}", data=json.dumps(data), headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK

    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.json.get("orgType") == OrgType.PREMIUM.value

    data["typeCode"] = OrgType.STAFF.value
    rv = client.put(f"/api/v1/orgs/{org_id}", data=json.dumps(data), headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK

    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.json.get("orgType") == OrgType.PREMIUM.value


def test_get_org_payment_settings(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be updated via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.bcol_linked()), headers=headers, content_type="application/json"
    )

    assert schema_utils.validate(rv.json, "org_response")[0]
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json.get("orgType") == OrgType.PREMIUM.value

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)

    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]
    rv = client.get(f"/api/v1/orgs/{org_id}/contacts", headers=headers)
    assert schema_utils.validate(rv.json, "contacts")[0]


def test_update_org_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can not be updated and return 400 error via PUT."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.put(
        f"/api/v1/orgs/{org_id}",
        data=json.dumps(TestOrgInfo.invalid),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_update_org_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that attempting to update a non-existent org returns a 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.put(
        f"/api/v1/orgs/{999}",
        data=json.dumps(TestOrgInfo.org1),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_update_org_returns_exception(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that attempting to update a non-existent org returns an exception."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    with patch.object(OrgService, "update_org", side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)):
        rv = client.put(
            f"/api/v1/orgs/{org_id}",
            data=json.dumps(TestOrgInfo.org1),
            headers=headers,
            content_type="application/json",
        )
        assert rv.status_code == 400
        assert schema_utils.validate(rv.json, "exception")[0]


def test_add_contact(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED
    dictionary = json.loads(rv.data)
    assert dictionary["email"] == TestContactInfo.contact1["email"]
    assert schema_utils.validate(rv.json, "contact_response")[0]


def test_add_contact_invalid_format_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that adding an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.invalid),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_contact_valid_email_returns_201(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that adding an valid formatted contact with special characters in email returns a 201."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.email_valid),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED
    assert schema_utils.validate(rv.json, "contacts")[0]


def test_add_contact_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact to a non-existant org returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(
        f"/api/v1/orgs/{99}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_add_contact_duplicate_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that adding a duplicate contact to an org returns 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    rv = client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_update_contact(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can be updated on an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED

    rv = client.put(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact2),
        content_type="application/json",
    )

    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "contact_response")[0]
    dictionary = json.loads(rv.data)
    assert dictionary["email"] == TestContactInfo.contact2["email"]


def test_update_contact_invalid_format_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that updating with an invalidly formatted contact returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    rv = client.put(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.invalid),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_update_contact_valid_email_format_returns_200(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that updating with an validly formatted contact with special characters in email returns a 200."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    rv = client.put(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.email_valid),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "contact_response")[0]


def test_update_contact_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that updating a contact on a non-existant entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.put(
        f"/api/v1/orgs/{99}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_update_contact_missing_returns_404(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that updating a non-existant contact returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.put(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_delete_contact(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a contact can be deleted on an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED

    rv = client.delete(
        f"/api/v1/orgs/{org_id}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact2),
        content_type="application/json",
    )

    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "contact_response")[0]

    rv = client.get(f"/api/v1/orgs/{org_id}/contacts", headers=headers)

    dictionary = None
    dictionary = json.loads(rv.data)

    assert len(dictionary["contacts"]) == 0


def test_delete_contact_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that deleting a contact on a non-existant entity returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.delete(
        f"/api/v1/orgs/{99}/contacts",
        headers=headers,
        data=json.dumps(TestContactInfo.contact1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_delete_contact_returns_exception(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that attempting to delete an org returns an exception."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    with patch.object(OrgService, "delete_contact", side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)):
        rv = client.delete(f"/api/v1/orgs/{org_id}/contacts", headers=headers, content_type="application/json")
        assert rv.status_code == 400
        assert schema_utils.validate(rv.json, "exception")[0]


def test_get_members(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a list of members for an org can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]
    # Create API_GW user, this shouldn't show up in the users list
    user_dict = dict(TestUserInfo.user1)
    user_dict["login_source"] = LoginSource.API_GW.value
    api_user = factory_user_model(user_dict)
    factory_membership_model(api_user.id, org_id=org_id)

    rv = client.get(f"/api/v1/orgs/{org_id}/members", headers=headers, content_type="application/json")

    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "members")[0]
    dictionary = json.loads(rv.data)
    assert dictionary["members"]
    assert len(dictionary["members"]) == 1
    assert dictionary["members"][0]["membershipTypeCode"] == "ADMIN"


@pytest.mark.parametrize(
    "test_scenario,expected_affidavit_status",
    [("single_org", AffidavitStatus.INACTIVE.value), ("multiple_orgs", AffidavitStatus.APPROVED.value)],
)
def test_delete_org(client, jwt, session, keycloak_mock, monkeypatch, test_scenario, expected_affidavit_status):  # pylint:disable=unused-argument
    """Assert that an org can be deleted with proper affidavit handling."""
    patch_pay_account_delete(monkeypatch)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    user = client.post("/api/v1/users", headers=headers, content_type="application/json")
    user_id = user.json.get("id")

    affidavit = AffidavitModel(
        document_id=str(uuid.uuid4()),
        issuer="TEST",
        status_code=AffidavitStatus.APPROVED.value,
        user_id=user_id,
    ).save()
    affidavit_id = affidavit.id

    # Create first organization
    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.bceid_org_with_all_info),
        headers=headers,
        content_type="application/json",
    )
    org_id = org_response.json.get("id")

    if test_scenario == "multiple_orgs":
        second_org_payload = TestOrgInfo.bceid_org_with_all_info.copy()
        second_org_payload["name"] = FAKE.name()
        second_org_response = client.post(
            "/api/v1/orgs",
            data=json.dumps(second_org_payload),
            headers=headers,
            content_type="application/json",
        )
        second_org_id = second_org_response.json.get("id")
        # Add user as admin to second org
        factory_membership_model(user_id, second_org_id, "ADMIN")

    rv = client.delete(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.NO_CONTENT

    assert AffidavitModel.find_by_id(affidavit_id).status_code == expected_affidavit_status

    if test_scenario == "multiple_orgs":
        remaining_orgs = MembershipModel.find_orgs_for_user(user_id)
        unique_orgs = list({org.id: org for org in remaining_orgs}.values())
        assert len(unique_orgs) == 1
        assert unique_orgs[0].id == second_org_id


def test_delete_org_failures(client, jwt, session, keycloak_mock, monkeypatch):  # pylint:disable=unused-argument
    """Assert that an org cannot be deleted."""
    patch_pay_account_delete_error(monkeypatch)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]
    rv = client.delete(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.BAD_REQUEST
    assert rv.json.get("code") == "OUTSTANDING_CREDIT"


def test_get_invitations(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a list of invitations for an org can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        "/api/v1/invitations",
        data=json.dumps(factory_invitation(org_id, "abc123@email.com")),
        headers=headers,
        content_type="application/json",
    )

    rv = client.post(
        "/api/v1/invitations",
        data=json.dumps(factory_invitation(org_id, "xyz456@email.com")),
        headers=headers,
        content_type="application/json",
    )

    rv = client.get(f"/api/v1/orgs/{org_id}/invitations", headers=headers, content_type="application/json")

    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "invitations")[0]
    dictionary = json.loads(rv.data)
    assert dictionary["invitations"]
    assert len(dictionary["invitations"]) == 2
    assert dictionary["invitations"][0]["recipientEmail"] == "abc123@email.com"
    assert dictionary["invitations"][1]["recipientEmail"] == "xyz456@email.com"


def test_update_member(client, jwt, session, auth_mock, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a member of an org can have their role updated."""
    # Set up: create/login user, create org
    headers_invitee = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers_invitee, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers_invitee, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    # Invite a user to the org
    rv = client.post(
        "/api/v1/invitations",
        data=json.dumps(factory_invitation(org_id, "abc123@email.com")),
        headers=headers_invitee,
        content_type="application/json",
    )
    dictionary = json.loads(rv.data)
    invitation_id = dictionary["id"]
    invitation_id_token = InvitationService.generate_confirmation_token(invitation_id)

    # Create/login as invited user
    headers_invited = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_role_2)
    rv = client.post("/api/v1/users", headers=headers_invited, content_type="application/json")

    # Accept invite as invited user
    rv = client.put(
        f"/api/v1/invitations/tokens/{invitation_id_token}",
        headers=headers_invited,
        content_type="application/json",
    )

    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert dictionary["status"] == "ACCEPTED"

    # Get pending members for the org as invitee and assert length of 1
    rv = client.get(f"/api/v1/orgs/{org_id}/members?status=PENDING_APPROVAL", headers=headers_invitee)
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert dictionary["members"]
    assert len(dictionary["members"]) == 1

    # Find the pending member
    new_member = dictionary["members"][0]
    assert new_member["membershipTypeCode"] == "USER"
    member_id = new_member["id"]

    # Update the new member
    rv = client.patch(
        f"/api/v1/orgs/{org_id}/members/{member_id}",
        headers=headers_invitee,
        data=json.dumps({"role": "COORDINATOR"}),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "membership")[0]
    dictionary = json.loads(rv.data)
    assert dictionary["membershipTypeCode"] == "COORDINATOR"


def test_add_affiliation(client, jwt, session, keycloak_mock, entity_mapping_mock):  # pylint:disable=unused-argument
    """Assert that a contact can be added to an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.entity_lear_mock),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        headers=headers,
        data=json.dumps(TestAffliationInfo.affiliation3),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED
    assert schema_utils.validate(rv.json, "affiliation_response")[0]

    dictionary = json.loads(rv.data)
    assert dictionary["organization"]["id"] == org_id


def test_add_affiliation_invalid_format_returns_400(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that adding an invalidly formatted affiliations returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        headers=headers,
        data=json.dumps(TestAffliationInfo.invalid),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_affiliation_no_org_returns_404(client, jwt, session):  # pylint:disable=unused-argument
    """Assert that adding a contact to a non-existant org returns 404."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post(
        f"/api/v1/orgs/{99}/affiliations",
        headers=headers,
        data=json.dumps(TestAffliationInfo.affiliation1),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_add_affiliation_returns_exception(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that attempting to delete an affiliation returns an exception."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post(
        "/api/v1/entities", data=json.dumps(TestEntityInfo.entity1), headers=headers, content_type="application/json"
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    with patch.object(
        AffiliationService, "create_affiliation", side_effect=BusinessException(Error.DATA_ALREADY_EXISTS, None)
    ):
        rv = client.post(
            f"/api/v1/orgs/{org_id}/affiliations",
            data=json.dumps(TestAffliationInfo.affiliation1),
            headers=headers,
            content_type="application/json",
        )
        assert rv.status_code == 400
        assert schema_utils.validate(rv.json, "exception")[0]


def test_add_new_business_affiliation_staff(client, jwt, session, keycloak_mock, nr_mock, entity_mapping_mock):
    """Assert that an affiliation can be added by staff."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.entity_lear_mock),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    convert_org_to_staff_org(org_id, OrgType.SBC_STAFF.value)

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_business)
    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations?newBusiness=true",
        headers=headers,
        data=json.dumps(TestAffliationInfo.new_business_affiliation),
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED
    assert schema_utils.validate(rv.json, "affiliation_response")[0]
    certified_by_name = TestAffliationInfo.new_business_affiliation["certifiedByName"]

    dictionary = json.loads(rv.data)
    assert dictionary["organization"]["id"] == org_id
    assert dictionary["certifiedByName"] == certified_by_name

    rv = client.get(f"/api/v1/orgs/{org_id}/affiliations", headers=headers)
    assert rv.status_code == HTTPStatus.OK

    assert schema_utils.validate(rv.json, "affiliations_response")[0]
    affiliations = json.loads(rv.data)

    assert affiliations["entities"][0]["affiliations"][0]["certifiedByName"] == certified_by_name


def test_get_affiliation(client, jwt, session, keycloak_mock, entity_mapping_mock):  # pylint:disable=unused-argument
    """Assert that a list of affiliation for an org can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.name_request),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        data=json.dumps(TestAffliationInfo.nr_affiliation),
        headers=headers,
        content_type="application/json",
    )

    assert rv.status_code == HTTPStatus.CREATED

    business_identifier = TestAffliationInfo.nr_affiliation["businessIdentifier"]

    rv = client.get(f"/api/v1/orgs/{org_id}/affiliations/{business_identifier}", headers=headers)
    assert rv.status_code == HTTPStatus.OK

    dictionary = json.loads(rv.data)
    assert dictionary["business"]["businessIdentifier"] == business_identifier


def test_get_affiliation_without_authorized(client, jwt, session, keycloak_mock, entity_mapping_mock):  # pylint:disable=unused-argument
    """Assert that a list of affiliation for an org can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.name_request),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        data=json.dumps(TestAffliationInfo.nr_affiliation),
        headers=headers,
        content_type="application/json",
    )

    assert rv.status_code == HTTPStatus.CREATED

    business_identifier = TestAffliationInfo.nr_affiliation["businessIdentifier"]

    headers = factory_auth_header(
        jwt=jwt, claims=TestJwtClaims.get_test_real_user(sub="a8098c1a-f86e-11da-bd1a-00112444be1e")
    )
    rv = client.get(f"/api/v1/orgs/{org_id}/affiliations/{business_identifier}", headers=headers)
    assert rv.status_code == HTTPStatus.UNAUTHORIZED

    headers = factory_auth_header(
        jwt=jwt, claims=TestJwtClaims.get_test_real_user(sub="a8098c1a-f86e-11da-bd1a-00112444be1d")
    )
    rv = client.get(f"/api/v1/orgs/{org_id}/affiliations/search", headers=headers)
    assert rv.status_code == HTTPStatus.FORBIDDEN

    headers = factory_auth_header(
        jwt=jwt, claims=TestJwtClaims.get_test_real_user(sub="a8098c1a-f86e-11da-bd1a-00112444be1d")
    )
    rv = client.get(f"/api/v1/orgs/{org_id}/affiliations?new=true", headers=headers)
    assert rv.status_code == HTTPStatus.FORBIDDEN


def test_get_affiliations(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a list of affiliation for an org can be retrieved."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.entity_lear_mock),
        headers=headers,
        content_type="application/json",
    )
    rv = client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.entity_lear_mock2),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        data=json.dumps(TestAffliationInfo.affiliation3),
        headers=headers,
        content_type="application/json",
    )
    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        data=json.dumps(TestAffliationInfo.affiliation4),
        headers=headers,
        content_type="application/json",
    )

    rv = client.get(f"/api/v1/orgs/{org_id}/affiliations", headers=headers)
    assert rv.status_code == HTTPStatus.OK

    assert schema_utils.validate(rv.json, "affiliations_response")[0]
    affiliations = json.loads(rv.data)
    # Result is sorted desc order of created date
    assert affiliations["entities"][1]["businessIdentifier"] == TestEntityInfo.entity_lear_mock["businessIdentifier"]
    assert affiliations["entities"][0]["businessIdentifier"] == TestEntityInfo.entity_lear_mock2["businessIdentifier"]


def test_search_orgs_for_affiliation(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that search org with affiliation works."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.entity_lear_mock),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        headers=headers,
        data=json.dumps(TestAffliationInfo.affiliation3),
        content_type="application/json",
    )
    # Create a system token
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.get(
        "/api/v1/orgs?affiliation={}".format(TestAffliationInfo.affiliation3.get("businessIdentifier")),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "orgs_response")[0]

    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("name") == TestOrgInfo.org1.get("name")


def test_unauthorized_search_orgs_for_affiliation(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that search org with affiliation works."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.entity_lear_mock),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        headers=headers,
        data=json.dumps(TestAffliationInfo.affiliation3),
        content_type="application/json",
    )
    # Create a system token
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.edit_user_role)
    rv = client.get(
        "/api/v1/orgs?affiliation={}".format(TestAffliationInfo.affiliation3.get("businessIdentifier")),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_add_bcol_linked_org(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.bcol_linked()), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    assert schema_utils.validate(rv.json, "org_response")[0]
    assert rv.json.get("orgType") == OrgType.PREMIUM.value
    assert rv.json.get("name") == TestOrgInfo.bcol_linked()["name"]

    # assert user have access to VS, as this bcol linked user have VS access
    org_id = rv.json.get("id")
    rv = client.get(
        f"/api/v1/orgs/{org_id}/products?includeInternal=false",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    has_vs_access: bool = False
    for product in json.loads(rv.data):
        if product.get("code") == ProductCode.VS.value:
            has_vs_access = product.get("subscriptionStatus") == ProductSubscriptionStatus.ACTIVE.value
    assert has_vs_access, "test vs access"

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)

    org_search_response = client.get(
        f"/api/v1/orgs?name={TestOrgInfo.bcol_linked()['name']}", headers=headers, content_type="application/json"
    )

    assert len(org_search_response.json.get("orgs")) == 1
    assert org_search_response.status_code == HTTPStatus.OK

    orgs = json.loads(org_search_response.data)
    assert orgs.get("orgs")[0].get("name") == TestOrgInfo.bcol_linked()["name"]
    account_id = orgs.get("orgs")[0].get("bcolAccountId")

    # do a search with bcol account id and name
    org_search_response = client.get(
        f"/api/v1/orgs?name={TestOrgInfo.bcol_linked()['name']}&bcolAccountId={account_id}",
        headers=headers,
        content_type="application/json",
    )
    orgs = json.loads(org_search_response.data)
    assert orgs.get("orgs")[0].get("name") == TestOrgInfo.bcol_linked()["name"]
    new_account_id = orgs.get("orgs")[0].get("bcolAccountId")
    assert account_id == new_account_id


def test_add_bcol_linked_org_failure_mailing_address(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.bcol_linked_incomplete_mailing_addrees()),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_add_bcol_linked_org_different_name(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be POSTed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.bcol_linked_different_name()),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED


@pytest.mark.parametrize(
    "test_name, nr_status, payment_status, error",
    [
        ("NR_Approved", NRStatus.APPROVED.value, "COMPLETED", None),
        ("NR_Draft", NRStatus.DRAFT.value, "COMPLETED", None),
        ("NR_Draft", NRStatus.DRAFT.value, "REJECTED", Error.NR_NOT_PAID),
        ("NR_Consumed", NRStatus.CONSUMED.value, "COMPLETED", Error.NR_INVALID_STATUS),
    ],
)
def test_new_business_affiliation(
    client, jwt, session, keycloak_mock, entity_mapping_mock, mocker, test_name, nr_status, payment_status, error
):
    """Assert that an NR can be affiliated to an org."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    nr_response = {
        "applicants": {
            "emailAddress": "",
            "phoneNumber": TestAffliationInfo.nr_affiliation["phone"],
        },
        "names": [{"name": "TEST INC.", "state": nr_status}],
        "state": nr_status,
        "requestTypeCd": "BC",
    }

    payment_response = {"invoices": [{"statusCode": payment_status}]}

    mocker.patch("auth_api.services.affiliation.Affiliation._get_nr_details", return_value=nr_response)

    mocker.patch("auth_api.services.affiliation.Affiliation.get_nr_payment_details", return_value=payment_response)

    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations?newBusiness=true",
        headers=headers,
        data=json.dumps(TestAffliationInfo.nr_affiliation),
        content_type="application/json",
    )

    if error is None:
        assert rv.status_code == HTTPStatus.CREATED
        assert schema_utils.validate(rv.json, "affiliation_response")[0]
        dictionary = json.loads(rv.data)
        assert dictionary["organization"]["id"] == org_id
        assert dictionary["business"]["businessIdentifier"] == TestAffliationInfo.nr_affiliation["businessIdentifier"]
    else:
        assert rv.status_code == error.status_code
        assert rv.json["message"] == error.message


def test_get_org_admin_affidavits(client, jwt, session, keycloak_mock, gcs_mock):
    """Assert that staff admin can get pending affidavits."""
    # Setup
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    admin_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    # 1. Create User
    client.post("/api/v1/users", headers=user_headers, content_type="application/json")

    # 2. Get document signature
    doc_response = client.get(
        "/api/v1/documents/test.jpeg/signatures", headers=user_headers, content_type="application/json"
    )
    assert doc_response.status_code == HTTPStatus.OK
    assert "key" in doc_response.json
    assert doc_response.json["key"] is not None
    doc_key = doc_response.json.get("key")

    # 3. Create affidavit
    affidavit_data = TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)
    affidavit_response = client.post(
        f"/api/v1/users/{TestJwtClaims.public_user_role.get('sub')}/affidavits",
        headers=user_headers,
        data=json.dumps(affidavit_data),
        content_type="application/json",
    )
    assert affidavit_response.status_code == HTTPStatus.OK

    # 4. Create Org
    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=user_headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED
    org_id = org_response.json.get("id")

    # 5. Get affidavits as admin
    staff_response = client.get(
        f"/api/v1/orgs/{org_id}/admins/affidavits",
        headers=admin_headers,
        content_type="application/json",
    )
    assert staff_response.status_code == HTTPStatus.OK

    # Debug output
    print("Response data:", staff_response.json)

    # Schema validation
    is_valid, errors = schema_utils.validate(staff_response.json, "affidavit_response")
    if not is_valid:
        print("Schema validation errors:", errors)
    assert is_valid

    # Data assertions
    assert staff_response.json.get("documentId") == doc_key
    assert staff_response.json.get("id") == affidavit_response.json.get("id")


def test_approve_org_with_pending_affidavits(client, jwt, session, keycloak_mock, gcs_mock):
    """Assert that staff admin can approve pending affidavits."""
    # 1. Setup user and headers
    user_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    staff_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    admin_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    # 2. Create test user
    client.post("/api/v1/users", headers=user_headers, content_type="application/json")

    # 3. Add contact info
    client.post(
        "/api/v1/users/contacts",
        data=json.dumps(TestContactInfo.contact1),
        headers=user_headers,
        content_type="application/json",
    )

    # 4. Create document signature (mock this if needed)
    doc_response = client.get(
        "/api/v1/documents/test.jpeg/signatures", headers=user_headers, content_type="application/json"
    )
    assert doc_response.status_code == HTTPStatus.OK
    doc_key = doc_response.json.get("key")

    # 5. Create affidavit
    affidavit_response = client.post(
        f"/api/v1/users/{TestJwtClaims.public_user_role.get('sub')}/affidavits",
        headers=user_headers,
        data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
        content_type="application/json",
    )
    assert affidavit_response.status_code == HTTPStatus.OK

    # 6. Create org (should be PENDING_STAFF_REVIEW)
    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=user_headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED
    org_id = org_response.json.get("id")

    # Verify initial status
    org = client.get(f"/api/v1/orgs/{org_id}", headers=user_headers)
    assert org.json.get("orgStatus") == OrgStatus.PENDING_STAFF_REVIEW.value

    # 7. Find and approve the task
    tasks = TaskService.fetch_tasks(TaskSearch(status=[TaskStatus.OPEN.value]))
    assert len(tasks["tasks"]) > 0

    task_id = tasks["tasks"][0]["id"]
    approval_response = client.put(
        f"/api/v1/tasks/{task_id}",
        data=json.dumps(
            {
                "status": TaskStatus.COMPLETED.value,
                "relationshipStatus": TaskRelationshipStatus.ACTIVE.value,
                # Add any required approval details here
            }
        ),
        headers=staff_headers,
        content_type="application/json",
    )
    assert approval_response.status_code == HTTPStatus.OK

    # 8. Verify org status changed to ACTIVE
    org = client.get(f"/api/v1/orgs/{org_id}", headers=user_headers)
    assert org.json.get("orgStatus") == OrgStatus.ACTIVE.value, (
        f"Expected ACTIVE status, got {org.json.get('orgStatus')}"
    )

    # 9. Verify affidavit status
    staff_response = client.get(
        f"/api/v1/orgs/{org_id}/admins/affidavits",
        headers=admin_headers,
        content_type="application/json",
    )
    assert staff_response.status_code == HTTPStatus.OK
    assert staff_response.json.get("status") == AffidavitStatus.APPROVED.value


@pytest.mark.skip(reason="Fix this later")
def test_approve_org_with_pending_affidavits_duplicate_affidavit(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that staff admin can approve pending affidavits."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Get the affidavit as a bcol admin
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    # POST a contact to test user
    client.post(
        "/api/v1/users/contacts",
        data=json.dumps(TestContactInfo.contact1),
        headers=headers,
        content_type="application/json",
    )

    document_signature = client.get(
        "/api/v1/documents/test.jpeg/signatures", headers=headers, content_type="application/json"
    )
    doc_key = document_signature.json.get("key")
    new_contact_email = "test@test.com"
    issuer = "New_Issuer"

    client.post(
        "/api/v1/users/{}/affidavits".format(TestJwtClaims.public_user_role.get("sub")),
        headers=headers,
        data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
        content_type="application/json",
    )
    document_signature2 = client.get(
        "/api/v1/documents/test2.jpeg/signatures", headers=headers, content_type="application/json"
    )
    doc_key2 = document_signature2.json.get("key")
    affidavit_response_second_time = client.post(
        "/api/v1/users/{}/affidavits".format(TestJwtClaims.public_user_role.get("sub")),
        headers=headers,
        data=json.dumps(
            TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key2, email=new_contact_email, issuer=issuer)
        ),
        content_type="application/json",
    )

    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED

    task_search = TaskSearch(status=[TaskStatus.OPEN.value], page=1, limit=10)

    tasks = TaskService.fetch_tasks(task_search)
    fetched_task = tasks["tasks"][0]

    update_task_payload = {
        "status": TaskStatus.COMPLETED.value,
        "relationshipStatus": TaskRelationshipStatus.ACTIVE.value,
    }

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_role)
    rv = client.put(
        "/api/v1/tasks/{}".format(fetched_task["id"]),
        data=json.dumps(update_task_payload),
        headers=headers,
        content_type="application/json",
    )

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    rv = client.get(
        "/api/v1/orgs/{}".format(org_response.json.get("id")), headers=headers, content_type="application/json"
    )

    assert rv.json.get("orgStatus") == OrgStatus.ACTIVE.value

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    affidavit_staff_response = client.get(
        "/api/v1/orgs/{}/admins/affidavits".format(org_response.json.get("id")),
        headers=headers,
        content_type="application/json",
    )

    assert schema_utils.validate(affidavit_staff_response.json, "affidavit_response")[0]
    assert affidavit_staff_response.json.get("documentId") == doc_key2
    assert affidavit_staff_response.json.get("id") == affidavit_response_second_time.json.get("id")
    assert affidavit_staff_response.json.get("status") == AffidavitStatus.APPROVED.value
    assert affidavit_staff_response.json.get("issuer") == issuer
    assert affidavit_staff_response.json.get("contacts")[0].get("email") == new_contact_email


def test_suspend_unsuspend(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that staff admin can approve pending affidavits."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Get the affidavit as a bcol admin
    public_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post("/api/v1/users", headers=public_headers, content_type="application/json")

    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=public_headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps(
            {"statusCode": OrgStatus.SUSPENDED.value, "suspensionReasonCode": SuspensionReasonCode.OWNER_CHANGE.name}
        ),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.json.get("orgStatus") == OrgStatus.SUSPENDED.value
    assert org_patch_response.json.get("suspensionReasonCode") == SuspensionReasonCode.OWNER_CHANGE.name

    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps({"statusCode": OrgStatus.ACTIVE.value}),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.json.get("orgStatus") == OrgStatus.ACTIVE.value

    # public user suspending/unsuspend shud give back error

    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps({"statusCode": OrgStatus.SUSPENDED.value}),
        headers=public_headers,
        content_type="application/json",
    )
    assert org_patch_response.status_code == HTTPStatus.UNAUTHORIZED

    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps({"statusCode": OrgStatus.ACTIVE.value}),
        headers=public_headers,
        content_type="application/json",
    )
    assert org_patch_response.status_code == HTTPStatus.UNAUTHORIZED


def test_org_suspended_reason(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be retrieved via GET."""
    public_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post("/api/v1/users", headers=public_headers, content_type="application/json")

    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=public_headers,
        content_type="application/json",
    )
    dictionary = json.loads(org_response.data)
    org_id = dictionary["id"]
    assert org_response.status_code == HTTPStatus.CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps(
            {"statusCode": OrgStatus.SUSPENDED.value, "suspensionReasonCode": SuspensionReasonCode.OWNER_CHANGE.name}
        ),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.json.get("orgStatus") == OrgStatus.SUSPENDED.value
    assert org_patch_response.json.get("suspensionReasonCode") == SuspensionReasonCode.OWNER_CHANGE.name

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "org_response")[0]
    dictionary = json.loads(rv.data)
    assert dictionary["suspensionReasonCode"] == SuspensionReasonCode.OWNER_CHANGE.name


def test_search_orgs_with_pending_affidavits(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that staff admin can approve pending affidavits."""
    # 1. Create User
    # 2. Get document signed link
    # 3. Create affidavit
    # 4. Create Org
    # 5. Get the affidavit as a bcol admin
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    document_signature = client.get(
        "/api/v1/documents/test.jpeg/signatures", headers=headers, content_type="application/json"
    )
    doc_key = document_signature.json.get("key")
    client.post(
        "/api/v1/users/{}/affidavits".format(TestJwtClaims.public_user_role.get("sub")),
        headers=headers,
        data=json.dumps(TestAffidavit.get_test_affidavit_with_contact(doc_id=doc_key)),
        content_type="application/json",
    )

    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    org_search_response = client.get(
        "/api/v1/orgs?status=PENDING_STAFF_REVIEW", headers=headers, content_type="application/json"
    )

    assert len(org_search_response.json.get("orgs")) == 1
    assert schema_utils.validate(org_search_response.json, "paged_response")[0]


def test_search_org_pagination(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that pagination works."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    client.post("/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json")
    client.post("/api/v1/orgs", data=json.dumps(TestOrgInfo.org2), headers=headers, content_type="application/json")
    client.post("/api/v1/orgs", data=json.dumps(TestOrgInfo.org3), headers=headers, content_type="application/json")

    # staff search
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get("/api/v1/orgs?page=1&limit=10", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 3
    assert len(orgs.get("orgs")) == 3

    rv = client.get("/api/v1/orgs?page=1&limit=2", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 3
    assert len(orgs.get("orgs")) == 2


def test_search_org_invitations(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that org search includes invitations for PENDING_ACTIVATION GOVM orgs."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")

    # Create two GOVM orgs (created with PENDING_INVITE_ACCEPT status)
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org_govm), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    dictionary = json.loads(rv.data)
    org_id_1 = dictionary["id"]
    rv = client.post(
        "/api/v1/invitations",
        data=json.dumps(factory_invitation(org_id=org_id_1)),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED

    rv = client.post(
        "/api/v1/orgs",
        data=json.dumps({**TestOrgInfo.org_govm, "name": "Second GOVM Org"}),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED
    dictionary = json.loads(rv.data)
    org_id_2 = dictionary["id"]
    rv = client.post(
        "/api/v1/invitations",
        data=json.dumps(factory_invitation(org_id=org_id_2)),
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.CREATED

    # Staff search with PENDING_ACTIVATION status to include invitations
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    rv = client.get(
        "/api/v1/orgs?status=PENDING_ACTIVATION",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK

    orgs = json.loads(rv.data)
    assert len(orgs.get("orgs")) == 2
    assert len(orgs.get("orgs")[0].get("invitations")) == 1


def test_delete_affiliation_no_payload(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an affiliation for an org can be removed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.entity_lear_mock),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        data=json.dumps(TestAffliationInfo.affiliation3),
        headers=headers,
        content_type="application/json",
    )

    rv = client.get(f"/api/v1/orgs/{org_id}/affiliations", headers=headers)
    assert rv.status_code == HTTPStatus.OK

    assert schema_utils.validate(rv.json, "affiliations_response")[0]
    affiliations = json.loads(rv.data)
    # Result is sorted desc order of created date
    assert affiliations["entities"][0]["businessIdentifier"] == TestEntityInfo.entity_lear_mock["businessIdentifier"]

    affiliation_id = affiliations["entities"][0]["businessIdentifier"]
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    da = client.delete(
        f"/api/v1/orgs/{org_id}/affiliations/{affiliation_id}",
        headers=headers,
        content_type="application/json",
    )
    assert da.status_code == HTTPStatus.OK


def test_delete_affiliation_payload_no_mail(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an affiliation for an org can be removed."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv = client.post(
        "/api/v1/entities",
        data=json.dumps(TestEntityInfo.entity_lear_mock),
        headers=headers,
        content_type="application/json",
    )
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    rv = client.post(
        f"/api/v1/orgs/{org_id}/affiliations",
        data=json.dumps(TestAffliationInfo.affiliation3),
        headers=headers,
        content_type="application/json",
    )

    rv = client.get(f"/api/v1/orgs/{org_id}/affiliations", headers=headers)
    assert rv.status_code == HTTPStatus.OK

    assert schema_utils.validate(rv.json, "affiliations_response")[0]
    affiliations = json.loads(rv.data)
    # Result is sorted desc order of created date
    assert affiliations["entities"][0]["businessIdentifier"] == TestEntityInfo.entity_lear_mock["businessIdentifier"]

    affiliation_id = affiliations["entities"][0]["businessIdentifier"]
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    da = client.delete(
        f"/api/v1/orgs/{org_id}/affiliations/{affiliation_id}",
        headers=headers,
        data=json.dumps(DeleteAffiliationPayload.delete_affiliation2),
        content_type="application/json",
    )
    assert da.status_code == HTTPStatus.OK


def test_org_patch_validate_request_json(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Validate patch org endpoints based on different input."""
    public_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post("/api/v1/users", headers=public_headers, content_type="application/json")

    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=public_headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED

    # Validate public Bcol user cannot do patch
    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps(
            {"statusCode": OrgStatus.SUSPENDED.value, "suspensionReasonCode": SuspensionReasonCode.OWNER_CHANGE.name}
        ),
        headers=public_headers,
        content_type="application/json",
    )
    assert org_patch_response.status_code == HTTPStatus.UNAUTHORIZED

    # Validate patch - update status fails if it is missing one of json properties
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)
    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps({"statusCode": OrgStatus.SUSPENDED.value}),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.status_code == HTTPStatus.BAD_REQUEST

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)
    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps({"suspensionReasonCode": SuspensionReasonCode.OWNER_CHANGE.name}),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.status_code == HTTPStatus.BAD_REQUEST

    # Validate patch - update access type fails if it is missing one of json properties
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)
    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps({"action": PatchActions.UPDATE_ACCESS_TYPE.value, "accessType": AccessType.GOVM.value}),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.status_code == HTTPStatus.BAD_REQUEST

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)
    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps({"action": PatchActions.UPDATE_ACCESS_TYPE.value}),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.status_code == HTTPStatus.BAD_REQUEST


def test_org_patch_access_type(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert patch Org endpoint for access type."""
    public_headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_bceid_user)
    client.post("/api/v1/users", headers=public_headers, content_type="application/json")

    org_response = client.post(
        "/api/v1/orgs",
        data=json.dumps(TestOrgInfo.org_with_mailing_address()),
        headers=public_headers,
        content_type="application/json",
    )
    assert org_response.status_code == HTTPStatus.CREATED

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.bcol_admin_role)

    org_patch_response = client.patch(
        "/api/v1/orgs/{}".format(org_response.json.get("id")),
        data=json.dumps({"action": PatchActions.UPDATE_ACCESS_TYPE.value, "accessType": AccessType.GOVN.value}),
        headers=headers,
        content_type="application/json",
    )
    assert org_patch_response.json.get("accessType") == AccessType.GOVN.value


def test_search_org_govm(client, jwt, session, monkeypatch):  # pylint:disable=unused-argument
    """Create org_govm, find it in the search."""
    # Set up: create/login user, create org
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")

    # Create govm organization.
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org_govm), headers=headers, content_type="application/json"
    )

    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    # Invite a user to the org
    rv = client.post(
        "/api/v1/invitations",
        data=json.dumps(factory_invitation(org_id, "abc123@email.com", membership_type=ADMIN)),
        headers=headers,
        content_type="application/json",
    )

    # Fetch PENDING_ACTIVATION for govm.
    rv = client.get("/api/v1/orgs?status=PENDING_ACTIVATION", headers=headers)
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert dictionary["orgs"]
    assert len(dictionary["orgs"]) == 1

    # 1 - assert org can be deleted without any dependencies like members or business affiliations.
    patch_pay_account_delete(monkeypatch)

    # Delete PENDING_INVITE_ACCEPT org.
    rv = client.delete(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.NO_CONTENT


def test_new_active_search(client, jwt, session, keycloak_mock):
    """Check for id, accessType , orgType, decisionMadeBy."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org_premium), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED

    dictionary = json.loads(rv.data)
    org_id_1 = dictionary["id"]
    decision_made_by = "barney"
    org: OrgModel = OrgModel.find_by_org_id(org_id_1)
    org.decision_made_by = decision_made_by
    org.status_code = OrgStatus.ACTIVE.value
    org.save()

    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org_regular), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org_govm), headers=headers, content_type="application/json"
    )
    assert rv.status_code == HTTPStatus.CREATED

    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]
    org: OrgModel = OrgModel.find_by_org_id(org_id)
    org.status_code = OrgStatus.ACTIVE.value
    org.save()

    # staff search
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)

    # # Fetch by Id
    rv = client.get(f"/api/v1/orgs?id={org_id_1}&status=ACTIVE", headers=headers)
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("id") == org_id_1

    # Fetch by accessType
    rv = client.get(f"/api/v1/orgs?accessType={AccessType.GOVM.value}&status=ACTIVE", headers=headers)
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("accessType") == AccessType.GOVM.value

    # Fetch by orgType
    rv = client.get(f"/api/v1/orgs?orgType={OrgType.PREMIUM.value}&status=ACTIVE", headers=headers)
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("orgType") == OrgType.PREMIUM.value

    # Fetch by decisionMadeBy
    rv = client.get(f"/api/v1/orgs?decisionMadeBy={decision_made_by}&status=ACTIVE", headers=headers)
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "paged_response")[0]
    orgs = json.loads(rv.data)
    assert orgs.get("orgs")[0].get("decisionMadeBy") == decision_made_by


@pytest.mark.parametrize(
    "test_name, businesses, drafts, drafts_with_nrs, nrs, dates",
    [
        ("businesses_only", [("BC1234567", CorpType.BC.value), ("BC1234566", CorpType.BC.value)], [], [], [], []),
        (
            "drafts_only",
            [],
            [
                ("T12dfhsff1", CorpType.BC.value, CorpType.TMP.value),
                ("T12dfhsff2", CorpType.GP.value, CorpType.RTMP.value),
            ],
            [],
            [],
            [],
        ),
        ("nrs_only", [], [], [], [("NR 1234567", "NEW"), ("NR 1234566", "NEW")], []),
        (
            "drafts_with_nrs",
            [],
            [],
            [
                ("T12dfhsff1", CorpType.BC.value, CorpType.TMP.value, "NR 1234567"),
                ("T12dfhsff2", CorpType.GP.value, CorpType.RTMP.value, "NR 1234566"),
            ],
            [("NR 1234567"), ("NR 1234566")],
            [],
        ),
        (
            "affiliations_order",
            [],
            [],
            [],
            [
                ("abcde1", CorpType.BC.value, "NR 123456"),
                ("abcde2", CorpType.BC.value, "NR 123457"),
                ("abcde3", CorpType.BC.value, "NR 123458"),
                ("abcde4", CorpType.BC.value, "NR 123459"),
            ],
            [datetime(2021, 1, 1), datetime(2022, 2, 1), datetime(2022, 3, 1), datetime(2023, 2, 1)],
        ),
        (
            "all",
            [("BC1234567", CorpType.BC.value), ("BC1234566", CorpType.BC.value)],
            [
                ("T12dfhsff1", CorpType.BC.value, CorpType.TMP.value),
                ("T12dfhsff2", CorpType.GP.value, CorpType.RTMP.value),
            ],
            [
                ("T12dfhsff3", CorpType.BC.value, CorpType.TMP.value, "NR 1234567"),
                ("T12dfhsff4", CorpType.GP.value, CorpType.RTMP.value, "NR 1234566"),
            ],
            [("NR 1234567"), ("NR 1234566"), ("NR 1234565")],
            [datetime(2021, 1, 1), datetime(2022, 2, 1)],
        ),
    ],
)
def test_get_org_affiliations(
    client, jwt, session, keycloak_mock, mocker, test_name, businesses, drafts, drafts_with_nrs, nrs, dates
):
    """Assert details of affiliations for an org are returned."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    # setup org
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    # setup mocks
    businesses_details = [
        {
            "adminFreeze": False,
            "goodStanding": True,
            "identifier": data[0],
            "legalName": "KIALS BUSINESS NAME CORP.",
            "legalType": data[1],
            "state": "ACTIVE",
            "taxId": "123",
        }
        for data in businesses
    ]

    drafts_details = [
        {
            "identifier": data[0],
            "legalType": data[1],
            "draftType": data[2],
        }
        for data in drafts
    ]

    drafts_with_nr_details = [
        {"identifier": data[0], "legalType": data[1], "draftType": data[2], "nrNumber": data[3]}
        for data in drafts_with_nrs
    ]

    nrs_details = {
        "hasMore": False,
        "requests": [
            {
                "actions": [],
                "applicants": {
                    "emailAddress": "1@1.com",
                    "phoneNumber": "1234567890",
                },
                "names": [{"name": f"TEST INC. {nr}", "state": "APPROVED"}],
                "stateCd": "APPROVED",
                "requestTypeCd": "BC",
                "request_action_cd": nr[1],
                "nrNum": nr,
            }
            for nr in nrs
        ],
    }
    # Add dates to nrs_details
    for i, date in enumerate(dates):
        if i < len(nrs_details["requests"]):
            nrs_details["requests"][i]["created"] = date.isoformat()

    entities_response = {
        "businessEntities": businesses_details,
        "draftEntities": drafts_details + drafts_with_nr_details,
    }

    nrs_response = nrs_details

    # mock function that calls namex / lear
    mocker.patch(
        "auth_api.services.rest_service.RestService.call_posts_in_parallel",
        return_value=[entities_response, nrs_response],
    )
    mocker.patch("auth_api.services.rest_service.RestService.get_service_account_token", return_value="token")

    for search_type in ["affiliations/search", "affiliations?new=true"]:
        rv = client.get(f"/api/v1/orgs/{org_id}/{search_type}", headers=headers, content_type="application/json")

        assert rv.status_code == HTTPStatus.OK
        assert rv.json.get("entities", None) and isinstance(rv.json["entities"], list)
        assert len(rv.json["entities"]) == len(businesses) + len(drafts) + len(nrs)

        drafts_nr_numbers = [data[3] for data in drafts_with_nrs]
        for entity in rv.json["entities"]:
            if entity["legalType"] == CorpType.NR.value:
                assert entity["nameRequest"]["nrNum"] not in drafts_nr_numbers

            if draft_type := entity.get("draftType", None):
                expected = (
                    CorpType.RTMP.value
                    if entity["legalType"] in [CorpType.SP.value, CorpType.GP.value]
                    else CorpType.TMP.value
                )
                if entity.get("nameRequest", {}).get("requestActionCd") == NRActionCodes.AMALGAMATE.value:
                    expected = CorpType.ATMP.value

                assert draft_type == expected

        # Assert that the entities are sorted in descending order of creation dates
        if test_name == "affiliations_order" and len(dates) > 0:
            created_order = [affiliation["nameRequest"].get("created") for affiliation in rv.json["entities"]]
            dates.sort()
            date_iso = [date.isoformat() for date in dates]
            assert date_iso == created_order


def _create_orgs_entities_and_affiliations(client, jwt, count):
    created_orgs = []
    for i in range(0, count):
        headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
        client.post(
            "/api/v1/entities",
            data=json.dumps(TestEntityInfo.entity_lear_mock),
            headers=headers,
            content_type="application/json",
        )

        headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
        client.post("/api/v1/users", headers=headers, content_type="application/json")
        new_org = TestOrgInfo.org_details.copy()
        new_org["name"] = new_org["name"] + " " + str(i)
        new_org["branchName"] = "branch-for-" + new_org["name"]
        rv = client.post("/api/v1/orgs", data=json.dumps(new_org), headers=headers, content_type="application/json")
        dictionary = json.loads(rv.data)
        org_id = dictionary["id"]
        new_org["id"] = org_id
        created_orgs.append(new_org)

        client.post(
            f"/api/v1/orgs/{org_id}/affiliations",
            headers=headers,
            data=json.dumps(TestAffliationInfo.affiliation3),
            content_type="application/json",
        )

    return created_orgs


@pytest.mark.parametrize(
    "expected_http_status, entries_count",
    [
        (HTTPStatus.OK, 1),
        (HTTPStatus.OK, 3),
        (HTTPStatus.OK, 0),
    ],
    ids=[
        "Assert that fetching orgs filtered by business identifier works, single entry.",
        "Assert that fetching orgs filtered by business identifier works, multiple entries.",
        "Assert that fetching orgs filtered by business identifier works, no entry",
    ],
)
def test_get_orgs_by_affiliation(client, jwt, session, keycloak_mock, expected_http_status, entries_count):
    """Assert that api call returns affiliated orgs."""
    created_orgs = _create_orgs_entities_and_affiliations(client, jwt, entries_count)

    # Create a system token
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.get(
        "/api/v1/orgs/affiliation/{}".format(TestAffliationInfo.affiliation3.get("businessIdentifier")),
        headers=headers,
        content_type="application/json",
    )

    response = json.loads(rv.data)

    assert rv.status_code == expected_http_status
    assert schema_utils.validate(rv.json, "orgs_response")[1]
    assert len(response.get("orgsDetails")) == entries_count
    orgs_details = response.get("orgsDetails")

    for co in created_orgs:
        names = [od["name"] for od in orgs_details]
        branches = [od["branchName"] for od in orgs_details]
        assert co["name"] in names
        assert co["branchName"] in branches

    for od in orgs_details:
        assert "name" in od
        assert "branchName" in od
        assert "uuid" in od
        assert "id" not in od


def test_get_orgs_by_affiliation_filtering_out_staff_orgs(app, client, jwt, session, keycloak_mock):
    """Assert that fetching orgs by affiliation do not return staff orgs."""
    orig_val_max_number_of_orgs = app.config.get("MAX_NUMBER_OF_ORGS")
    app.config.update(MAX_NUMBER_OF_ORGS=10)
    create_org_count = 6

    created_orgs = _create_orgs_entities_and_affiliations(client, jwt, create_org_count)
    app.config.update(MAX_NUMBER_OF_ORGS=orig_val_max_number_of_orgs)

    org3 = created_orgs[2]
    org5 = created_orgs[4]

    convert_org_to_staff_org(org3["id"], OrgType.SBC_STAFF.value)
    convert_org_to_staff_org(org5["id"], OrgType.STAFF.value)

    staff_org_names = [org3["name"], org5["name"]]
    expected_org_count = create_org_count - len(staff_org_names)

    # Create a system token
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.system_role)
    rv = client.get(
        "/api/v1/orgs/affiliation/{}".format(TestAffliationInfo.affiliation3.get("businessIdentifier")),
        headers=headers,
        content_type="application/json",
    )

    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "orgs_response")[1]

    response = json.loads(rv.data)

    assert len(response.get("orgsDetails")) == expected_org_count  # without org 3 and 5
    orgs_details = response.get("orgsDetails")

    for od in orgs_details:
        assert od["name"] not in staff_org_names


def test_update_org_api_access(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that an org can be searched."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    rv = client.post(
        "/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json"
    )
    dictionary = json.loads(rv.data)
    org_id = dictionary["id"]

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_account_holder_user)
    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    assert schema_utils.validate(rv.json, "org_response")[0]
    dictionary = json.loads(rv.data)
    assert dictionary["id"] == org_id
    assert dictionary["hasApiAccess"] is False

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)
    client.patch(
        f"/api/v1/orgs/{org_id}",
        data=json.dumps({"hasApiAccess": True, "action": PatchActions.UPDATE_API_ACCESS.value}),
        headers=headers,
        content_type="application/json",
    )
    rv = client.get(f"/api/v1/orgs/{org_id}", headers=headers, content_type="application/json")
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert dictionary["hasApiAccess"] is True


def test_search_org_members(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that a list of members for an org search can be retrieved."""
    user_info = dict(TestJwtClaims.public_user_role)
    headers = factory_auth_header(jwt=jwt, claims=user_info)
    client.post("/api/v1/users", headers=headers, content_type="application/json")
    client.post("/api/v1/orgs", data=json.dumps(TestOrgInfo.org1), headers=headers, content_type="application/json")

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_view_accounts_role)
    rv = client.get(
        f"/api/v1/orgs?status=ACTIVE&includeMembers=true&members={user_info['preferred_username']}",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    dictionary = json.loads(rv.data)
    assert dictionary["orgs"]
    assert len(dictionary["orgs"][0]["members"]) == 1
    member = dictionary["orgs"][0]["members"][0]
    assert member["membershipTypeCode"] == "ADMIN"
    assert member["user"]
    user = member["user"]
    assert user["username"] == user_info["preferred_username"]

    rv = client.get(
        f"/api/v1/orgs?status=ACTIVE&includeMembers=true&members={user_info['lastname']} {user_info['firstname']}",
        headers=headers,
        content_type="application/json",
    )

    dictionary = json.loads(rv.data)
    assert dictionary["orgs"]
    assert len(dictionary["orgs"][0]["members"]) == 1
    member = dictionary["orgs"][0]["members"][0]
    assert member["membershipTypeCode"] == "ADMIN"
    assert member["user"]
    user = member["user"]
    assert user["firstname"] == user_info["firstname"]
    assert user["lastname"] == user_info["lastname"]

    rv = client.get(
        "/api/v1/orgs?status=ACTIVE&includeMembers=true&members=NOTHING",
        headers=headers,
        content_type="application/json",
    )
    dictionary = json.loads(rv.data)
    assert not dictionary["orgs"]


def test_search_org_suspended_filters(client, jwt, session, keycloak_mock):  # pylint:disable=unused-argument
    """Assert that orgs can be searched by suspended date and suspension reason code."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_manage_accounts_role)

    today = datetime.now(pytz.timezone("America/Vancouver"))
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    org1 = factory_org_model(org_info=TestOrgInfo.org1)
    org1.status_code = OrgStatus.SUSPENDED.value
    org1.suspended_on = yesterday
    org1.suspension_reason_code = SuspensionReasonCode.OWNER_CHANGE.name
    org1.save()

    org2 = factory_org_model(org_info=TestOrgInfo.org2)
    org2.status_code = OrgStatus.SUSPENDED.value
    org2.suspended_on = last_week
    org2.suspension_reason_code = SuspensionReasonCode.DISPUTE.name
    org2.save()

    org3 = factory_org_model(org_info=TestOrgInfo.org_with_mailing_address())
    org3.status_code = OrgStatus.SUSPENDED.value
    org3.suspended_on = today
    org3.suspension_reason_code = SuspensionReasonCode.OWNER_CHANGE.name
    org3.save()

    rv = client.get(
        f"/api/v1/orgs?status=SUSPENDED&suspensionReasonCode={SuspensionReasonCode.OWNER_CHANGE.name}",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 2
    org_ids = [org.get("id") for org in orgs.get("orgs")]
    assert org1.id in org_ids
    assert org3.id in org_ids
    assert org2.id not in org_ids

    rv = client.get(
        f"/api/v1/orgs?status=SUSPENDED&suspensionReasonCode={SuspensionReasonCode.DISPUTE.name}",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 1
    assert orgs.get("orgs")[0].get("id") == org2.id

    rv = client.get(
        f"/api/v1/orgs?status=SUSPENDED&suspendedDateFrom={yesterday.strftime('%Y-%m-%d')}",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 2
    org_ids = [org.get("id") for org in orgs.get("orgs")]
    assert org1.id in org_ids
    assert org3.id in org_ids
    assert org2.id not in org_ids

    rv = client.get(
        f"/api/v1/orgs?status=SUSPENDED&suspendedDateTo={yesterday.strftime('%Y-%m-%d')}",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 2
    org_ids = [org.get("id") for org in orgs.get("orgs")]
    assert org1.id in org_ids
    assert org2.id in org_ids
    assert org3.id not in org_ids

    rv = client.get(
        f"/api/v1/orgs?status=SUSPENDED&suspendedDateFrom={last_week.strftime('%Y-%m-%d')}&suspendedDateTo={yesterday.strftime('%Y-%m-%d')}",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 2
    org_ids = [org.get("id") for org in orgs.get("orgs")]
    assert org1.id in org_ids
    assert org2.id in org_ids
    assert org3.id not in org_ids

    rv = client.get(
        f"/api/v1/orgs?status=SUSPENDED&suspendedDateFrom={last_week.strftime('%Y-%m-%d')}&suspendedDateTo={yesterday.strftime('%Y-%m-%d')}&suspensionReasonCode={SuspensionReasonCode.OWNER_CHANGE.name}",
        headers=headers,
        content_type="application/json",
    )
    assert rv.status_code == HTTPStatus.OK
    orgs = json.loads(rv.data)
    assert orgs.get("total") == 1
    assert orgs.get("orgs")[0].get("id") == org1.id
