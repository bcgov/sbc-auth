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
"""Service for managing Organization data."""

from typing import Dict, Tuple

from flask import current_app
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.schemas import OrgSchema
from auth_api.utils.roles import OWNER, VALID_STATUSES, Status
from auth_api.utils.util import camelback2snake

from .authorization import check_auth
from .invitation import Invitation as InvitationService


class Org:
    """Manages all aspects of Org data.

    This service manages creating, updating, and retrieving Org data via the Org model.
    """

    def __init__(self, model):
        """Return an Org Service."""
        self._model = model

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the internal Org model as a dictionary.

        None fields are not included.
        """
        org_schema = OrgSchema()
        obj = org_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def create_org(org_info: dict, user_id):
        """Create a new organization."""
        current_app.logger.debug('<create_org ')
        existing_similar__org = OrgModel.find_similar_org_by_name(org_info['name'])
        if existing_similar__org is not None:
            raise BusinessException(Error.DATA_CONFLICT, None)

        org = OrgModel.create_from_dict(camelback2snake(org_info))
        org.save()
        current_app.logger.info(f'<created_org org_id:{org.id}')
        # create the membership record for this user
        membership = MembershipModel(org_id=org.id, user_id=user_id, membership_type_code='OWNER',
                                     membership_type_status=Status.ACTIVE.value)
        membership.save()

        return Org(org)

    def update_org(self, org_info):
        """Update the passed organization with the new info."""
        current_app.logger.debug('<update_org ')
        self._model.update_org_from_dict(camelback2snake(org_info))
        current_app.logger.debug('>update_org ')
        return self

    def delete_org(self):
        """Delete this org."""
        current_app.logger.debug('>delete_org ')
        self._model.delete()
        current_app.logger.debug('<delete_org ')

    @staticmethod
    def find_by_org_id(org_id, token_info: Dict = None, allowed_roles: Tuple = None):
        """Find and return an existing organization with the provided id."""
        if org_id is None:
            return None

        org_model = OrgModel.find_by_org_id(org_id)
        if not org_model:
            return None

        # Check authorization for the user
        check_auth(token_info, one_of_roles=allowed_roles, org_id=org_id)

        return Org(org_model)

    def add_contact(self, contact_info):
        """Create a new contact for this org."""
        # check for existing contact (only one contact per org for now)
        current_app.logger.debug('>add_contact ')
        contact_link = ContactLinkModel.find_by_org_id(self._model.id)
        if contact_link is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        contact = ContactModel(**camelback2snake(contact_info))
        contact.commit()

        contact_link = ContactLinkModel()
        contact_link.contact = contact
        contact_link.org = self._model
        contact_link.commit()
        current_app.logger.debug('>add_contact ')
        return self

    def update_contact(self, contact_info):
        """Update the existing contact for this org."""
        current_app.logger.debug('>update_contact ')
        contact_link = ContactLinkModel.find_by_org_id(self._model.id)
        if contact_link is None or contact_link.contact is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact = contact_link.contact
        contact.update_from_dict(**camelback2snake(contact_info))
        contact.commit()
        current_app.logger.debug('<update_contact ')
        return self

    def delete_contact(self):
        """Delete the contact for this org."""
        current_app.logger.debug('>delete_contact ')
        contact_link = ContactLinkModel.find_by_org_id(self._model.id)
        if contact_link is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        del contact_link.org
        contact_link.commit()

        if not contact_link.has_links():
            contact = contact_link.contact
            contact_link.delete()
            contact.delete()
        current_app.logger.debug('<delete_contact ')
        return self

    def get_invitations(self, status='ALL', token_info: Dict = None):
        """Return the unresolved (pending or failed) invitations for this org."""
        return {'invitations': InvitationService.get_invitations_by_org_id(self._model.id, status, token_info)}

    def get_owner_count(self):
        """Get the number of owners for the specified org."""
        return list(filter(lambda x: x.membership_type == OWNER, self._model.members)).count()

    @staticmethod
    def get_orgs(user_id):
        """Return the orgs associated with this user."""
        # TODO DO_NOT_USE this def if there is a database transaction involved,
        # as the below logic removes object from model
        orgs = MembershipModel.find_orgs_for_user(user_id)
        # because members are fetched using backpopulates,cant add these conditions programmatically.
        # so resorting to manually looping   # noqa:E501

        for org in orgs:
            # user can have multiple memberships.if the user getting denied first and added again,
            # it will be multiple memberships..filter out denied records # noqa:E501
            # fix for https://github.com/bcgov/entity/issues/1951   # noqa:E501
            org.members = list(
                filter(lambda member: (member.user_id == user_id and (member.status in VALID_STATUSES)), org.members))
        return orgs
