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

from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.schemas import OrgSchema
from auth_api.utils.util import camelback2snake


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
        org = OrgModel.create_from_dict(org_info=org_info)
        org.save()

        # create the membership record for this user
        membership = MembershipModel(org_id=org.id, user_id=user_id, membership_type_code='OWNER')
        membership.save()

        return Org(org)

    def update_org(self, org_info):
        """Update the passed organization with the new info."""
        self._model.update_org_from_dict(org_info)
        return self

    def delete_org(self):
        """Delete this org."""
        self._model.delete()

    @staticmethod
    def find_by_org_id(org_id):
        """Find and return an existing organization with the provided id."""
        if org_id is None:
            return None

        org_model = OrgModel.find_by_org_id(org_id)
        if not org_model:
            return None

        return Org(org_model)

    def add_contact(self, contact_info):
        """Create a new contact for this org."""
        # check for existing contact (only one contact per org for now)
        contact_link = ContactLinkModel.find_by_org_id(self._model.id)
        if contact_link is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        contact = ContactModel(**camelback2snake(contact_info))
        contact.commit()

        contact_link = ContactLinkModel()
        contact_link.contact = contact
        contact_link.org = self._model
        contact_link.commit()

        return self

    def update_contact(self, contact_info):
        """Update the existing contact for this org."""
        contact_link = ContactLinkModel.find_by_org_id(self._model.id)
        if contact_link is None or contact_link.contact is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact = contact_link.contact
        contact.update_from_dict(**camelback2snake(contact_info))
        contact.commit()

        return self

    def delete_contact(self):
        """Delete the contact for this org."""
        contact_link = ContactLinkModel.find_by_org_id(self._model.id)
        if contact_link is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        del contact_link.org
        contact_link.commit()

        if not contact_link.has_links():
            contact = contact_link.contact
            contact_link.delete()
            contact.delete()

        return self
