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
"""The Membership service.

This module manages the Membership Information between an org and a user.
"""
from typing import Dict

from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.models import Membership as MembershipModel
from auth_api.models import MembershipType as MembershipTypeModel
from auth_api.schemas import MembershipSchema
from auth_api.utils.roles import ADMIN, OWNER

from .authorization import check_auth


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Membership:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Manages all aspects of the Membership Entity.

    This manages storing the Membership in the cache,
    ensuring that the local cache is up to date,
    submitting changes back to all storage systems as needed.
    """

    def __init__(self, model):
        """Return a membership service object."""
        self._model = model

    def as_dict(self):
        """Return the Membership as a python dict.

        None fields are not included in the dict.
        """
        membership_schema = MembershipSchema()
        obj = membership_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def get_membership_type_by_code(type_code):
        """Get a membership type by the given code."""
        return MembershipTypeModel.get_membership_type_by_code(type_code=type_code)

    @classmethod
    def find_membership_by_id(cls, membership_id, token_info: Dict = None):
        """Retrieve a membership record by id."""
        membership = MembershipModel.find_membership_by_id(membership_id)

        if membership:
            # Ensure that this user is an ADMIN or OWNER on the org associated with this membership
            check_auth(org_id=membership.org_id, token_info=token_info, one_of_roles=(ADMIN, OWNER))
            return Membership(membership)
        return None

    def update_membership_role(self, updated_role: MembershipTypeModel, token_info: Dict = None):
        """Update an existing membership with the given role."""
        # Ensure that this user is an ADMIN or OWNER on the org associated with this membership
        check_auth(org_id=self._model.org_id, token_info=token_info, one_of_roles=(ADMIN, OWNER))
        self._model.membership_type = updated_role
        self._model.save()
        return self
