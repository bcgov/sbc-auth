# Copyright © 2019 Province of British Columbia
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
"""Service to invoke Rest services."""

from flask import current_app
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError

from auth_api.models import db
from auth_api.models.membership import Membership as MembershipModel
from auth_api.models.org import Org as OrgModel
from auth_api.models.permissions import Permissions as PermissionsModel
from auth_api.models.user import User as UserModel
from auth_api.utils.cache import cache
from auth_api.utils.enums import OrgStatus, Status
from auth_api.utils.roles import VALID_ORG_STATUSES
from auth_api.utils.user_context import UserContext, user_context


class Permissions:  # pylint: disable=too-few-public-methods
    """Service for user settings."""

    def __init__(self, model):
        """Return an Permissions Service."""
        self._model = model

    @classmethod
    def build_all_permission_cache(cls):
        """Build cache for all permission values."""
        try:
            permissions: list[PermissionsModel] = PermissionsModel.get_all_permissions()
            per_kv: dict[tuple[str, int], list[str]] = {}
            for perm in permissions:
                key_tuple = (perm.org_status_code, perm.membership_type_code)
                actions_v: list = per_kv.get(key_tuple)
                if actions_v:
                    actions_v.append(perm.actions)
                    per_kv.update({key_tuple: actions_v})
                else:
                    per_kv[key_tuple] = [perm.actions]

            for key, val in per_kv.items():
                cache.set(key, val)

        except SQLAlchemyError as e:
            current_app.logger.info("Error on building cache %s", e)

    @staticmethod
    def get_permissions_for_membership(
        org_status, membership_type, user_model: UserModel = None, include_all_permissions: bool = False
    ):
        """Get the permissions for the membership type."""
        # Just a tweak til we get all org status to DB
        # TODO fix this logic
        if org_status not in (
            OrgStatus.NSF_SUSPENDED.value,
            OrgStatus.PENDING_STAFF_REVIEW.value,
            OrgStatus.SUSPENDED.value,
        ):
            org_status = None
        key_tuple = (org_status, membership_type)
        actions_from_cache = cache.get(key_tuple)

        additional_permissions = []
        if include_all_permissions:
            additional_permissions = Permissions.get_additional_user_permissions(user_model)
        if actions_from_cache:
            actions = actions_from_cache + additional_permissions
        else:
            permissions = PermissionsModel.get_permissions_by_membership(org_status, membership_type)
            actions = []
            for permission in permissions:
                actions.append(permission.actions)
        return actions + additional_permissions

    @staticmethod
    @user_context
    def get_additional_user_permissions(user_model: UserModel, **kwargs):
        """Check for and append additional permissions based on user type."""
        user_from_context: UserContext = kwargs["user_context"]
        additional_permissions = []
        if user_from_context.is_staff() or user_from_context.is_external_staff():
            additional_permissions = Permissions.get_permissions_by_org_type_membership(user_model.identifier)

        return additional_permissions

    @staticmethod
    def get_permissions_by_org_type_membership(user_id: int):
        """Retrieve permissions based on membership and org type."""
        permissions_query = (
            select(PermissionsModel.actions)
            .select_from(MembershipModel)
            .join(OrgModel, OrgModel.id == MembershipModel.org_id)
            .join(PermissionsModel, PermissionsModel.membership_type_code == OrgModel.type_code)
            .filter(OrgModel.status_code.in_(VALID_ORG_STATUSES))
            .filter(and_(MembershipModel.user_id == user_id, MembershipModel.status == Status.ACTIVE.value))
        )

        return db.session.scalars(permissions_query).all()
