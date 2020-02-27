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

from typing import Any, Dict, Tuple

from flask import current_app
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Contact as ContactModel
from auth_api.models import ProductCode as ProductCodeModel
from auth_api.models import ProductRoleCode as ProductRoleCodeModel
from auth_api.models import ProductRole as ProductRoleModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import User as UserModel
from auth_api.models import ProductSubscription as ProductSubscriptionModel
from auth_api.schemas import OrgSchema
from auth_api.utils.roles import OWNER, VALID_STATUSES, Status, AccessType
from auth_api.utils.util import camelback2snake

from .authorization import check_auth
from .contact import Contact as ContactService
from .keycloak import KeycloakService


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
    def create_org(org_info: dict, user_id, token_info: Dict = None):
        """Create a new organization."""
        current_app.logger.debug('<create_org ')
        is_staff = 'staff' in token_info.get('realm_access').get('roles')
        if not is_staff:  # staff can create any number of orgs
            count = OrgModel.get_count_of_org_created_by_user_id(user_id)
            if count >= current_app.config.get('MAX_NUMBER_OF_ORGS'):
                raise BusinessException(Error.MAX_NUMBER_OF_ORGS_LIMIT, None)

        existing_similar__org = OrgModel.find_similar_org_by_name(org_info['name'])
        if existing_similar__org is not None:
            raise BusinessException(Error.DATA_CONFLICT, None)

        org = OrgModel.create_from_dict(camelback2snake(org_info))
        org.save()
        current_app.logger.info(f'<created_org org_id:{org.id}')
        # create the membership record for this user if its not created by staff and access_type is anonymous
        if not is_staff and org_info.get('access_type') != AccessType.ANONYMOUS:
            membership = MembershipModel(org_id=org.id, user_id=user_id, membership_type_code='OWNER',
                                         membership_type_status=Status.ACTIVE.value)
            membership.save()

            # Add the user to account_holders group
            KeycloakService.join_account_holders_group()

        return Org(org)

    @staticmethod
    def create_product_subscription(subscription_data: Tuple[Dict[str, Any]], org_id):
        """creates product subscription for the user

        create product subscription first
        create the product role next if roles are given
        """
        org = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        subscriptions_list = subscription_data.get('subscriptions')
        for subscription in subscriptions_list:
            product_code = subscription.get('product_code')
            product = ProductCodeModel.find_by_code(product_code)
            if product:
                product_subscription = ProductSubscriptionModel(org_id=org_id, product_code=product_code).save()
            else:
                raise BusinessException(Error.DATA_NOT_FOUND, None)
            for role in subscription.get('product_roles'):
                product_role_code = ProductRoleCodeModel.find_by_code_and_product_code(role, product_code)
                if product_role_code:
                    ProductRoleModel(product_subscription_id=product_subscription.id,
                                     product_role_id=product_role_code.id).save()
        # TODO return the whole model
        return str(product_subscription.id)

    def update_org(self, org_info):
        """Update the passed organization with the new info."""
        current_app.logger.debug('<update_org ')

        existing_similar__org = OrgModel.find_similar_org_by_name(org_info['name'])
        if existing_similar__org is not None:
            raise BusinessException(Error.DATA_CONFLICT, None)

        self._model.update_org_from_dict(camelback2snake(org_info))
        current_app.logger.debug('>update_org ')
        return self

    @staticmethod
    def delete_org(org_id, token_info: Dict = None, ):
        """Soft-Deletes an Org.

        It should not be deletable if there are members or business associated with the org
        """
        # Check authorization for the user
        current_app.logger.debug('<org Inactivated')
        check_auth(token_info, one_of_roles=OWNER, org_id=org_id)

        org: OrgModel = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        count_members = len([member for member in org.members if member.status in VALID_STATUSES])
        if count_members > 1 or len(org.affiliated_entities) >= 1:
            raise BusinessException(Error.ORG_CANNOT_BE_DISSOLVED, None)

        org.delete()

        # Remove user from thr group if the user doesn't have any other orgs membership
        user = UserModel.find_by_jwt_token(token=token_info)
        if len(MembershipModel.find_orgs_for_user(user.id)) == 0:
            KeycloakService.remove_from_account_holders_group(user.keycloak_guid)
        current_app.logger.debug('org Inactivated>')

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

    @staticmethod
    def get_contacts(org_id):
        """Get the contacts for the given org."""
        current_app.logger.debug('get_contacts>')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        collection = []
        for contact_link in org.contacts:
            collection.append(ContactService(contact_link.contact).as_dict())
        return {'contacts': collection}

    @staticmethod
    def add_contact(org_id, contact_info):
        """Create a new contact for this org."""
        # check for existing contact (only one contact per org for now)
        current_app.logger.debug('>add_contact')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact_link = ContactLinkModel.find_by_org_id(org_id)
        if contact_link is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        contact = ContactModel(**camelback2snake(contact_info))
        contact = contact.flush()
        contact.commit()

        contact_link = ContactLinkModel()
        contact_link.contact = contact
        contact_link.org = org
        contact_link = contact_link.flush()
        contact_link.commit()
        current_app.logger.debug('<add_contact')

        return ContactService(contact)

    @staticmethod
    def update_contact(org_id, contact_info):
        """Update the existing contact for this org."""
        current_app.logger.debug('>update_contact ')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # find the contact link for this org
        contact_link = ContactLinkModel.find_by_org_id(org_id)
        if contact_link is None or contact_link.contact is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        contact = contact_link.contact
        contact.update_from_dict(**camelback2snake(contact_info))
        contact.commit()
        current_app.logger.debug('<update_contact ')

        # return the updated contact
        return ContactService(contact)

    @staticmethod
    def delete_contact(org_id):
        """Delete the contact for this org."""
        current_app.logger.debug('>delete_contact ')
        org = OrgModel.find_by_org_id(org_id)
        if not org or not org.contacts:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        deleted_contact = Org.__delete_contact(org)
        current_app.logger.debug('<delete_contact ')

        return ContactService(deleted_contact)

    @staticmethod
    def __delete_contact(org):
        # unlink the org from its contact
        contact_link = ContactLinkModel.find_by_org_id(org.id)
        if contact_link:
            del contact_link.org
            contact_link.commit()
            # clean up any orphaned contacts and links
            if not contact_link.has_links():
                contact = contact_link.contact
                contact_link.delete()
                contact.delete()
                return contact
        return None

    def get_owner_count(self):
        """Get the number of owners for the specified org."""
        return len([x for x in self._model.members if x.membership_type_code == OWNER])

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

    @staticmethod
    def search_orgs(**kwargs):
        """Search for orgs based on input parameters."""
        orgs = {'orgs': []}
        if kwargs.get('business_identifier', None):
            affiliation: AffiliationModel = AffiliationModel.\
                find_affiliations_by_business_identifier(kwargs.get('business_identifier'))
            if affiliation:
                orgs['orgs'].append(Org(OrgModel.find_by_org_id(affiliation.org_id)).as_dict())
        return orgs
