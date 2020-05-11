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
import json
from typing import Dict, Tuple

from flask import current_app
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api import status as http_status
from auth_api.exceptions import BusinessException, CustomException
from auth_api.exceptions.errors import Error
from auth_api.models import AccountPaymentSettings as AccountPaymentModel
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import User as UserModel
from auth_api.schemas import OrgSchema
from auth_api.utils.enums import PaymentType, OrgType, ChangeType
from auth_api.utils.roles import OWNER, VALID_STATUSES, Status, AccessType
from auth_api.utils.util import camelback2snake
from .authorization import check_auth
from .contact import Contact as ContactService
from .keycloak import KeycloakService
from .rest_service import RestService


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
    def create_org(org_info: dict, user_id,  # pylint: disable=too-many-locals, too-many-statements
                   token_info: Dict = None, bearer_token: str = None):
        """Create a new organization."""
        current_app.logger.debug('<create_org ')
        bcol_credential = org_info.pop('bcOnlineCredential', None)
        mailing_address = org_info.pop('mailingAddress', None)
        bcol_account_number = None
        bcol_user_id = None

        # If the account is created using BCOL credential, verify its valid bc online account
        if bcol_credential:
            bcol_response = Org.get_bcol_details(bcol_credential, org_info, bearer_token).json()
            bcol_account_number = bcol_response.get('accountNumber')
            bcol_user_id = bcol_response.get('userId')

        org_info['typeCode'] = OrgType.PREMIUM.value if bcol_account_number else OrgType.BASIC.value

        is_staff_admin = token_info and 'staff_admin' in token_info.get('realm_access').get('roles')
        if not is_staff_admin:  # staff can create any number of orgs
            count = OrgModel.get_count_of_org_created_by_user_id(user_id)
            if count >= current_app.config.get('MAX_NUMBER_OF_ORGS'):
                raise BusinessException(Error.MAX_NUMBER_OF_ORGS_LIMIT, None)
            if org_info.get('accessType', None) == AccessType.ANONYMOUS.value:
                raise BusinessException(Error.USER_CANT_CREATE_ANONYMOUS_ORG, None)

        if not bcol_account_number:  # Allow duplicate names if premium
            Org.raise_error_if_duplicate_name(org_info['name'])

        org = OrgModel.create_from_dict(camelback2snake(org_info))
        org.add_to_session()

        if is_staff_admin:
            org.access_type = AccessType.ANONYMOUS.value
            org.billable = False
        else:
            org.access_type = AccessType.BCSC.value
            org.billable = True

        # If mailing address is provided, save it
        if mailing_address:
            Org.add_contact_to_org(mailing_address, org)

        # create the membership record for this user if its not created by staff and access_type is anonymous
        if not is_staff_admin and org_info.get('access_type') != AccessType.ANONYMOUS:
            membership = MembershipModel(org_id=org.id, user_id=user_id, membership_type_code='OWNER',
                                         membership_type_status=Status.ACTIVE.value)
            membership.add_to_session()

            # Add the user to account_holders group
            KeycloakService.join_account_holders_group()

        Org.add_payment_settings(org.id, bcol_account_number, bcol_user_id)

        org.save()
        current_app.logger.info(f'<created_org org_id:{org.id}')

        return Org(org)

    @staticmethod
    def raise_error_if_duplicate_name(name):
        """Raise error if there is duplicate org name already."""
        existing_similar__org = OrgModel.find_similar_org_by_name(name)
        if existing_similar__org is not None:
            raise BusinessException(Error.DATA_CONFLICT, None)

    @staticmethod
    def add_payment_settings(org_id, bcol_account_number, bcol_user_id):
        """Add payment settings for the org."""
        payment_settings = AccountPaymentModel.create_from_dict({
            'org_id': org_id,
            'preferred_payment_code': PaymentType.BCOL.value if bcol_account_number else PaymentType.CREDIT_CARD.value,
            'bcol_user_id': bcol_user_id,
            'bcol_account_id': bcol_account_number
        })
        payment_settings.add_to_session()

    @staticmethod
    def get_bcol_details(bcol_credential: Dict, org_info: Dict = None, bearer_token: str = None, org_id=None):
        """Retrieve and validate BC Online credentials."""
        bcol_response = None
        if bcol_credential:
            bcol_response = RestService.post(endpoint=current_app.config.get('BCOL_API_URL') + '/profiles',
                                             data=bcol_credential, token=bearer_token, raise_for_status=False)

            if bcol_response.status_code != http_status.HTTP_200_OK:
                error = json.loads(bcol_response.text)
                raise BusinessException(CustomException(error['detail'], bcol_response.status_code), None)

            bcol_account_number = bcol_response.json().get('accountNumber')
            if org_info:
                if bcol_response.json().get('orgName') != org_info.get('name'):
                    raise BusinessException(Error.INVALID_INPUT, None)
            if Org.bcol_account_link_check(bcol_account_number, org_id):
                raise BusinessException(Error.BCOL_ACCOUNT_ALREADY_LINKED, None)
        return bcol_response

    def change_org_ype(self, org_info, action=None, bearer_token: str = None):
        """Update the passed organization with the new info.

        if Upgrade:
            //TODO .Missing RULES
            1.do bcol verification
            2.attach mailing
            3.change the org with bcol org name
        If downgrade:
            //TODO .Missing RULES
            1.remove contact
            2.deactivate payment settings
            3.add new payment settings for cc
            4.change the org with user passed org name

        """
        if self._model.access_type == AccessType.ANONYMOUS.value:
            raise BusinessException(Error.INVALID_INPUT, None)
        bcol_credential = org_info.pop('bcOnlineCredential', None)
        mailing_address = org_info.pop('mailingAddress', None)
        current_app.logger.debug('<update_org ', action)
        if action == ChangeType.DOWNGRADE.value:
            if org_info.get('typeCode') != OrgType.BASIC.value:
                raise BusinessException(Error.INVALID_INPUT, None)
            # if they have not changed the name , they can claim the name. Dont check duplicate..or else check duplicate
            if org_info.get('name') != self._model.name:
                Org.raise_error_if_duplicate_name(org_info['name'])
            payment_settings: AccountPaymentModel = AccountPaymentModel.find_active_by_org_id(account_id=self._model.id)
            payment_settings.is_active = False
            payment_settings.add_to_session()
            Org.add_payment_settings(self._model.id, None, None)
            Org.__delete_contact(self._model)

        if action == ChangeType.UPGRADE.value:
            if org_info.get('typeCode') != OrgType.PREMIUM.value or bcol_credential is None:
                raise BusinessException(Error.INVALID_INPUT, None)
            bcol_org_name = self.add_bcol_to_account(bcol_credential, bearer_token, org_info)
            org_info['name'] = bcol_org_name

            # If mailing address is provided, save it
            if mailing_address:
                self.add_contact_to_org(mailing_address, self._model)

        self._model.update_org_from_dict(camelback2snake(org_info), exclude=('status_code'))
        return self

    @staticmethod
    def add_contact_to_org(mailing_address, org):
        """Update the passed organization with the mailing address."""
        contact = ContactModel(**camelback2snake(mailing_address))
        contact = contact.add_to_session()
        contact_link = ContactLinkModel()
        contact_link.contact = contact
        contact_link.org = org
        contact_link.add_to_session()

    def update_org(self, org_info, bearer_token: str = None):
        """Update the passed organization with the new info."""
        current_app.logger.debug('<update_org ')

        if self._model.type_code != OrgType.PREMIUM.value:
            existing_similar__org = OrgModel.find_similar_org_by_name(org_info['name'], self._model.id)
            if existing_similar__org is not None:
                raise BusinessException(Error.DATA_CONFLICT, None)

        bcol_credential = org_info.pop('bcOnlineCredential', None)
        mailing_address = org_info.pop('mailingAddress', None)
        # If the account is created using BCOL credential, verify its valid bc online account
        # If it's a valid account disable the current one and add a new one
        if bcol_credential:
            self.add_bcol_to_account(bcol_credential, bearer_token, org_info)
        # Update mailing address
        if mailing_address:
            contact = self._model.contacts[0].contact
            contact.update_from_dict(**camelback2snake(mailing_address))
            contact.save()
        if self._model.type_code != OrgType.PREMIUM.value:
            self._model.update_org_from_dict(camelback2snake(org_info))
        current_app.logger.debug('>update_org ')
        return self

    def add_bcol_to_account(self, bcol_credential, bearer_token, org_info):
        """Add the passed organization with the bcol account details."""
        bcol_response = Org.get_bcol_details(bcol_credential, org_info, bearer_token, self._model.id).json()
        payment_settings: AccountPaymentModel = AccountPaymentModel.find_active_by_org_id(account_id=self._model.id)
        payment_settings.is_active = False
        payment_settings.add_to_session()
        Org.add_payment_settings(self._model.id, bcol_response.get('accountNumber'), bcol_response.get('userId'))
        return bcol_response.get('orgName')

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
    def get_payment_settings_for_org(org_id, token_info: Dict = None, allowed_roles: Tuple = None):
        """Get the payment settings for the given org."""
        current_app.logger.debug('get_payment_settings(>')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Check authorization for the user
        check_auth(token_info, one_of_roles=allowed_roles, org_id=org_id)
        return AccountPaymentModel.find_active_by_org_id(org_id)

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
    def get_orgs(user_id, valid_statuses=VALID_STATUSES):
        """Return the orgs associated with this user."""
        return MembershipModel.find_orgs_for_user(user_id, valid_statuses)

    @staticmethod
    def search_orgs(**kwargs):
        """Search for orgs based on input parameters."""
        orgs = {'orgs': []}
        if kwargs.get('business_identifier', None):
            affiliation: AffiliationModel = AffiliationModel. \
                find_affiliations_by_business_identifier(kwargs.get('business_identifier'))
            if affiliation:
                orgs['orgs'].append(Org(OrgModel.find_by_org_id(affiliation.org_id)).as_dict())
        elif kwargs.get('org_type', None):
            org_models = OrgModel.find_by_org_access_type(kwargs.get('org_type'))
            for org in org_models:
                orgs['orgs'].append(Org(org).as_dict())
        elif kwargs.get('name', None):
            org_model = OrgModel.find_similar_org_by_name(kwargs.get('name'))
            if org_model is not None:
                orgs['orgs'].append(Org(org_model).as_dict())
        return orgs

    @staticmethod
    def bcol_account_link_check(bcol_account_id, org_id=None):
        """Validate the BCOL id is linked or not. If already linked, return True."""
        if current_app.config.get('BCOL_ACCOUNT_LINK_CHECK'):
            account_payment = AccountPaymentModel.find_by_bcol_account_id(bcol_account_id, org_id)
            if account_payment:
                return True

        return False
