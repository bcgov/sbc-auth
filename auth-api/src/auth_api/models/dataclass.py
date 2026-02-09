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
"""This module holds data classes."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from requests import Request

from auth_api.utils.enums import KeycloakGroupActions
from auth_api.utils.serializable import Serializable


@dataclass
class Activity:
    """Used for Activity Log Publisher."""

    org_id: int
    action: str
    name: str
    value: str | None = None
    id: int | None = None
    type: str | None = None
    actor_id: int | None = None


@dataclass
class AffiliationInvitationSearch:  # pylint: disable=too-many-instance-attributes
    """Used for searching Affiliation Invitations."""

    status_codes: list[str] | None = None
    invitation_types: list[str] | None = None
    from_org_id: str | None = None
    to_org_id: str | None = None
    sender_id: str | None = None
    approver_id: str | None = None
    entity_id: str | None = None
    affiliation_id: str | None = None
    is_deleted: bool = False


@dataclass
class AffiliationSearchDetails:  # pylint: disable=too-many-instance-attributes
    """Used for filtering Affiliations based on filters passed."""

    page: int
    limit: int
    identifier: str | None = None
    status: str | None = None
    name: str | None = None
    type: str | None = None

    @classmethod
    def from_request_args(cls, req: Request) -> Self:
        """Used for searching affiliations."""
        return cls(
            identifier=req.args.get("identifier"),
            status=req.args.getlist("status") or [],
            name=req.args.get("name"),
            type=req.args.getlist("type") or [],
            page=int(req.args.get("page", 1)),
            limit=int(req.args.get("limit", 100000)),
        )


@dataclass
class AffiliationInvitationData:  # pylint: disable=too-many-instance-attributes
    """Used for as affiliation invitation DTO."""

    @dataclass
    class EntityDetails:
        """Used for as entity details in affiliation invitation DTO."""

        business_identifier: str
        name: str
        corp_type: str
        state: str
        corp_sub_type: str | None

    @dataclass
    class OrgDetails:
        """Used for as org details in affiliation invitation DTO."""

        id: str
        name: str

    id: str
    type: str
    affiliation_id: str
    business_identifier: str
    recipient_email: str
    sent_date: str
    accepted_date: str
    status: str
    additional_message: str

    from_org: OrgDetails
    to_org: OrgDetails
    entity: EntityDetails


@dataclass
class Affiliation:
    """Used for affiliation."""

    org_id: str
    business_identifier: str
    email: str | None = None
    phone: str | None = None
    certified_by_name: str | None = None


@dataclass
class DeleteAffiliationRequest:
    """Used for deleting affiliation."""

    org_id: str
    business_identifier: str
    email_addresses: str | None = None
    reset_passcode: bool = False
    log_delete_draft: bool = False


@dataclass
class OrgSearch:  # pylint: disable=too-many-instance-attributes
    """Used for searching organizations."""

    name: str
    branch_name: str
    business_identifier: str
    statuses: list[str] = field()
    access_type: list[str] = field()
    bcol_account_id: str
    id: str
    decision_made_by: str
    org_type: str
    include_members: bool
    member_search_text: str
    suspended_date_from: str
    suspended_date_to: str
    suspension_reason_code: str
    page: int
    limit: int


@dataclass
class SimpleOrgSearch:  # pylint: disable=too-many-instance-attributes
    """Used for searching organizations."""

    id: str
    name: str
    branch_name: str
    search_text: str
    statuses: list[str] = field()
    exclude_statuses: bool
    page: int
    limit: int


@dataclass
class TaskSearch:  # pylint: disable=too-many-instance-attributes
    """Used for searching tasks."""

    status: list[str] = field()
    relationship_status: str = ""
    name: str = ""
    start_date: str = ""
    end_date: str = ""
    type: str = ""
    modified_by: str = ""
    submitted_sort_order: str = "asc"
    page: int = 1
    limit: int = 10
    action: str = ""


@dataclass
class KeycloakGroupSubscription:
    """Used for entrying group subscriptions for keycloak."""

    user_guid: str
    product_code: str
    group_name: str
    group_action: KeycloakGroupActions


@dataclass
class ProductReviewTask:
    """Used for creating product subscription review task."""

    org_id: str
    org_name: str
    org_access_type: str
    product_code: str
    product_description: str
    product_subscription_id: int
    user_id: str
    external_source_id: str | None = None


@dataclass
class UnaffiliatedEmailInvitationData(Serializable):
    """Data for sending an unaffiliated email invitation to the mailer queue."""

    business_name: str
    email_addresses: str
    business_identifier: str
    token: str
    context_url: str


@dataclass
class AffiliationBase:
    """Small class for searching in Names and LEAR."""

    identifier: str
    created: datetime
