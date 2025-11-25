# Copyright © 2025 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""helper to publish to mailer."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Self

from flask import current_app
from simple_cloudevent import SimpleCloudEvent
from sqlalchemy import select

from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import User as UserModel
from auth_api.models import db
from auth_api.services.flags import flags
from auth_api.services.gcp_queue import GcpQueue, queue
from auth_api.services.user import User as UserService
from auth_api.utils.enums import CorpType, QueueSources, Status
from auth_api.utils.serializable import Serializable


@dataclass
class UserAffiliationEvent(Serializable):
    """User data for account events."""

    idp_userid: str | None
    login_source: str | None
    unaffiliated_identifiers: list[str] = field(default_factory=list)

    @classmethod
    def from_user_model(
        cls,
        user: UserModel,
        unaffiliated_identifiers: list[str],
    ) -> Self:
        """Create UserAffiliationEvent from UserModel."""
        return cls(
            idp_userid=user.idp_userid,
            login_source=user.login_source,
            unaffiliated_identifiers=unaffiliated_identifiers,
        )


@dataclass
class AccountEvent(Serializable):
    """Used account management queue messages."""

    account_id: int
    actioned_by: str
    action_category: str = "account-management"
    business_identifier: str | None = None
    user_affiliation_events: list[UserAffiliationEvent] | None = None


def publish_account_event(queue_message_type: str, data: AccountEvent, source: str = QueueSources.AUTH_API.value):
    """Publish to auth event topic."""
    payload = data.to_dict()
    cloud_event = SimpleCloudEvent(
        id=str(uuid.uuid4()),
        source=source,
        subject=None,
        time=datetime.now(tz=UTC).isoformat(),
        type=queue_message_type,
        data=payload,
    )
    try:
        kwargs = {}
        kwargs.update({"action_category": data.action_category})
        queue.publish(current_app.config.get("AUTH_EVENT_TOPIC"), GcpQueue.to_queue_message(cloud_event), **kwargs)
    except Exception as e:  # NOQA # pylint: disable=broad-except
        error_msg = f"Failed to publish to auth event topic {e}"
        current_app.logger.error(error_msg)


def _has_access_through_other_orgs(
    user_id, exclude_org_id: int, business_identifier: str = None, entity_id_column=None
):
    """Create EXISTS subquery to check if user has access to business through other orgs."""
    subquery = (
        select(1)
        .select_from(MembershipModel)
        .join(AffiliationModel, MembershipModel.org_id == AffiliationModel.org_id)
        .where(MembershipModel.user_id == user_id)
        .where(MembershipModel.status == Status.ACTIVE.value)
        .where(MembershipModel.org_id != exclude_org_id)
    )

    if business_identifier:
        subquery = subquery.join(EntityModel, AffiliationModel.entity_id == EntityModel.id).where(
            EntityModel.business_identifier == business_identifier
        )
    elif entity_id_column:
        subquery = subquery.where(AffiliationModel.entity_id == entity_id_column)

    return subquery.exists()


def _get_affiliation_event_users(org_id: int, business_identifier: str) -> list[UserAffiliationEvent]:
    """Get users with active membership in org and create UserAffiliationEvent with unaffiliated identifiers."""
    has_access_subquery = _has_access_through_other_orgs(UserModel.id, org_id, business_identifier)
    user_models = (
        db.session.query(UserModel)
        .join(MembershipModel, UserModel.id == MembershipModel.user_id)
        .filter(MembershipModel.org_id == org_id, MembershipModel.status == Status.ACTIVE.value)
        .filter(~has_access_subquery)
        .all()
    )

    return [
        UserAffiliationEvent.from_user_model(
            user,
            unaffiliated_identifiers=[business_identifier],
        )
        for user in user_models
    ]


def _get_team_member_unaffiliated_identifiers(user_id: int, org_id: int) -> list[UserAffiliationEvent]:
    """Get UserAffiliationEvent for a user losing access to an org with unaffiliated business identifiers."""
    has_access_subquery = _has_access_through_other_orgs(user_id, org_id, entity_id_column=EntityModel.id)
    user_model = UserModel.query.filter_by(id=user_id).first()
    # DBC has no interest in NR or TMP events.
    excluded_corp_types = [CorpType.NR.value, CorpType.TMP.value]
    unaffiliated_identifiers = (
        db.session.query(EntityModel.business_identifier)
        .join(AffiliationModel, AffiliationModel.entity_id == EntityModel.id)
        .filter(AffiliationModel.org_id == org_id)
        .filter(~EntityModel.corp_type_code.in_(excluded_corp_types))
        .filter(~has_access_subquery)
        .scalars()
    )

    return [UserAffiliationEvent.from_user_model(user_model, unaffiliated_identifiers=unaffiliated_identifiers)]


def _get_actioned_by() -> str | None:
    """Get the current user's identifier for actioned_by field."""
    current_user = UserService.find_by_jwt_token(silent_mode=True)
    return current_user.identifier if current_user else None


def publish_affiliation_event(queue_message_type: str, org_id: int, business_identifier: str):
    """Publish affiliation event to topic."""
    if not flags.is_on("enable-publish-account-events", default=False):
        return

    # DBC has no interest in NR or TMP events.
    if business_identifier.startswith("NR") or business_identifier.startswith("T"):
        return

    user_affiliation_events = _get_affiliation_event_users(org_id, business_identifier)
    publish_account_event(
        queue_message_type=queue_message_type,
        data=AccountEvent(
            account_id=org_id,
            business_identifier=business_identifier,
            actioned_by=_get_actioned_by(),
            user_affiliation_events=user_affiliation_events,
        ),
    )


def publish_team_member_event(queue_message_type: str, org_id: int, user_id: int):
    """Publish team member removed event to topic."""
    if not flags.is_on("enable-publish-account-events", default=False):
        return

    user_affiliation_events = _get_team_member_unaffiliated_identifiers(user_id, org_id)
    if not user_affiliation_events or not user_affiliation_events[0].unaffiliated_identifiers:
        return

    publish_account_event(
        queue_message_type=queue_message_type,
        data=AccountEvent(
            account_id=org_id,
            actioned_by=_get_actioned_by(),
            user_affiliation_events=user_affiliation_events,
        ),
    )
