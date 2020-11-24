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

from auth_api.models.permissions import Permissions as PermissionsModel
from ..utils.enums import OrgStatus


class Permissions:  # pylint: disable=too-few-public-methods
    """Service for user settings."""

    def __init__(self, model):
        """Return an Permissions Service."""
        self._model = model

    @staticmethod
    def get_permissions_for_membership(org_status, membership_type):
        """Get the permissions for the membership type."""
        # Just a tweak til we get all org status to DB
        # TODO fix this logic
        if org_status != OrgStatus.NSF_SUSPENDED.value:
            org_status = None
        permissions = PermissionsModel.get_permissions_by_membership(org_status,
                                                                     membership_type)
        actions = []
        for permission in permissions:
            actions.append(permission.actions)
        return actions
