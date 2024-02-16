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
from typing import Dict, List, Tuple

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from auth_api.models.permissions import Permissions as PermissionsModel

from ..utils.cache import cache
from ..utils.enums import OrgStatus


class Permissions:  # pylint: disable=too-few-public-methods
    """Service for user settings."""

    def __init__(self, model):
        """Return an Permissions Service."""
        self._model = model

    @classmethod
    def build_all_permission_cache(cls):
        """Build cache for all permission values."""
        try:
            permissions: List[PermissionsModel] = PermissionsModel.get_all_permissions()
            per_kv: Dict[Tuple[str, int], List[str]] = {}
            for perm in permissions:
                key_tuple = (perm.org_status_code, perm.membership_type_code)
                actions_v: List = per_kv.get(key_tuple)
                if actions_v:
                    actions_v.append(perm.actions)
                    per_kv.update({key_tuple: actions_v})
                else:
                    per_kv[key_tuple] = [perm.actions]

            for key, val in per_kv.items():
                cache.set(key, val)

        except SQLAlchemyError as e:
            current_app.logger.info('Error on building cache %s', e)

    @staticmethod
    def get_permissions_for_membership(org_status, membership_type):
        """Get the permissions for the membership type."""
        # Just a tweak til we get all org status to DB
        # TODO fix this logic
        if org_status not in (
                OrgStatus.NSF_SUSPENDED.value, OrgStatus.PENDING_STAFF_REVIEW.value, OrgStatus.SUSPENDED.value):
            org_status = None
        key_tuple = (org_status, membership_type)
        actions_from_cache = cache.get(key_tuple)
        if actions_from_cache:
            actions = actions_from_cache
        else:
            permissions = PermissionsModel.get_permissions_by_membership(org_status,
                                                                         membership_type)
            actions = []
            for permission in permissions:
                actions.append(permission.actions)
        return actions
