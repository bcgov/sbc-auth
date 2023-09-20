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

from typing import List, Optional
from dataclasses import dataclass, field

from auth_api.utils.enums import KeycloakGroupActions


@dataclass
class Activity:
    """Used for Activity Log Publisher."""

    org_id: int
    action: str
    name: str
    value: Optional[str] = None
    id: Optional[int] = None
    type: Optional[str] = None
    actor_id: Optional[int] = None


@dataclass
class PaginationInfo:
    """Used for providing pagination info."""

    page: int
    limit: int


@dataclass
class AffiliationInvitationSearch:  # pylint: disable=too-many-instance-attributes
    """Used for searching Affiliation Invitations."""

    status_codes: Optional[List[str]] = None
    invitation_types: Optional[List[str]] = None
    from_org_id: Optional[str] = None
    to_org_id: Optional[str] = None
    sender_id: Optional[str] = None
    approver_id: Optional[str] = None
    entity_id: Optional[str] = None
    affiliation_id: Optional[str] = None
    is_deleted: bool = False


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
        corp_sub_type: Optional[str]

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
    email: Optional[str] = None
    phone: Optional[str] = None
    certified_by_name: Optional[str] = None


@dataclass
class OrgSearch:  # pylint: disable=too-many-instance-attributes
    """Used for searching organizations."""

    name: str
    branch_name: str
    business_identifier: str
    statuses: List[str] = field()
    access_type: List[str] = field()
    bcol_account_id: str
    id: str
    decision_made_by: str
    org_type: str
    page: int
    limit: int


@dataclass
class TaskSearch:   # pylint: disable=too-many-instance-attributes
    """Used for searching tasks."""

    status: List[str] = field()
    relationship_status: str = ''
    name: str = ''
    start_date: str = ''
    end_date: str = ''
    type: str = ''
    modified_by: str = ''
    submitted_sort_order: str = 'asc'
    page: int = 1
    limit: int = 10


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
    product_code: str
    product_description: str
    product_subscription_id: int
    user_id: str
    external_source_id: Optional[str] = None
