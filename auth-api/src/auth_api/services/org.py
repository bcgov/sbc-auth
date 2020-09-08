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
from datetime import datetime
from typing import Dict, Tuple

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api import status as http_status
from auth_api.exceptions import BusinessException, CustomException
from auth_api.exceptions.errors import Error
from auth_api.models import AccountLoginOptions as AccountLoginOptionsModel
from auth_api.models import AccountPaymentSettings as AccountPaymentModel
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import User as UserModel
from auth_api.models.affidavit import Affidavit as AffidavitModel
from auth_api.schemas import ContactSchema, OrgSchema, InvitationSchema
from auth_api.utils.enums import (
    AccessType, ChangeType, LoginSource, OrgStatus, OrgType, PaymentType, ProductCode, Status)
from auth_api.utils.roles import ADMIN, VALID_STATUSES, Role, STAFF
from auth_api.utils.util import camelback2snake
from .affidavit import Affidavit as AffidavitService
from .authorization import check_auth
from .contact import Contact as ContactService
from .keycloak import KeycloakService
from .notification import send_email
from .products import Product as ProductService
from .rest_service import RestService

ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)


class Org:  # pylint: disable=too-many-public-methods
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
    def create_org(org_info: dict, user_id,  # pylint: disable=too-many-locals, too-many-statements, too-many-branches
                   token_info: Dict = None, bearer_token: str = None, origin_url: str = None):
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

        is_staff_admin = token_info and Role.STAFF_CREATE_ACCOUNTS.value in token_info.get('realm_access').get('roles')
        is_bceid_user = token_info and token_info.get('loginSource', None) == LoginSource.BCEID.value

        Org.validate_account_limit(is_staff_admin, user_id)

        access_type = Org.validate_access_type(is_bceid_user, is_staff_admin, org_info)

        if bcol_account_number is None:  # Allow duplicate names if premium
            Org.raise_error_if_duplicate_name(org_info['name'])

        org = OrgModel.create_from_dict(camelback2snake(org_info))
        org.access_type = access_type
        # If the account is anonymous set the billable value as False else True
        org.billable = access_type != AccessType.ANONYMOUS.value

        # Set the status based on access type
        # Check if the user is APPROVED else set the org status to PENDING
        # Send an email to staff to remind review the pending account
        if access_type in (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value) \
                and not AffidavitModel.find_approved_by_user_id(user_id=user_id):
            org.status_code = OrgStatus.PENDING_AFFIDAVIT_REVIEW.value
            user = UserModel.find_by_jwt_token(token=token_info)
            Org.send_staff_review_account_reminder(user, org.id, origin_url)

        # If mailing address is provided, save it
        if mailing_address:
            Org.add_contact_to_org(mailing_address, org)

        # create the membership record for this user if its not created by staff and access_type is anonymous
        Org.create_membership(access_type, is_staff_admin, org, user_id)

        Org.add_payment_settings(org.id, bcol_account_number, bcol_user_id)

        Org.add_product(org.id, token_info)

        org.commit()

        current_app.logger.info(f'<created_org org_id:{org.id}')

        return Org(org)

    @staticmethod
    def create_membership(access_type, is_staff_admin, org, user_id):
        """Create membership account."""
        if not is_staff_admin and access_type != AccessType.ANONYMOUS.value:
            membership = MembershipModel(org_id=org.id, user_id=user_id, membership_type_code='ADMIN',
                                         membership_type_status=Status.ACTIVE.value)
            membership.add_to_session()

            # Add the user to account_holders group
            KeycloakService.join_account_holders_group()

    @staticmethod
    def validate_account_limit(is_staff_admin, user_id):
        """Validate account limit."""
        if not is_staff_admin:  # staff can create any number of orgs
            count = OrgModel.get_count_of_org_created_by_user_id(user_id)
            if count >= current_app.config.get('MAX_NUMBER_OF_ORGS'):
                raise BusinessException(Error.MAX_NUMBER_OF_ORGS_LIMIT, None)

    @staticmethod
    def validate_access_type(is_bceid_user, is_staff_admin, org_info):
        """Validate and return access type."""
        access_type: str = org_info.get('accessType', None)
        if access_type:
            if not is_staff_admin and access_type == AccessType.ANONYMOUS.value:
                raise BusinessException(Error.USER_CANT_CREATE_ANONYMOUS_ORG, None)
            if not is_bceid_user and access_type in (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value):
                raise BusinessException(Error.USER_CANT_CREATE_EXTRA_PROVINCIAL_ORG, None)
            if is_bceid_user and access_type not in (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value):
                raise BusinessException(Error.USER_CANT_CREATE_REGULAR_ORG, None)
        else:
            # If access type is not provided, add default value based on user
            if is_staff_admin:
                access_type = AccessType.ANONYMOUS.value
            elif is_bceid_user:
                access_type = AccessType.EXTRA_PROVINCIAL.value
            else:
                access_type = AccessType.REGULAR.value
        return access_type

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
            'preferred_payment_code':
                PaymentType.BCOL.value if bcol_account_number else Org._get_default_payment_method_for_creditcard(),
            'bcol_user_id': bcol_user_id,
            'bcol_account_id': bcol_account_number
        })
        payment_settings.add_to_session()

    @staticmethod
    def _get_default_payment_method_for_creditcard():
        return PaymentType.DIRECT_PAY.value if current_app.config.get(
            'DIRECT_PAY_ENABLED') else PaymentType.CREDIT_CARD.value

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
        check_auth(token_info, one_of_roles=(ADMIN, STAFF), org_id=org_id)

        org: OrgModel = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        count_members = len([member for member in org.members if member.status in VALID_STATUSES])
        if count_members > 1 or len(org.affiliated_entities) >= 1:
            raise BusinessException(Error.ORG_CANNOT_BE_DISSOLVED, None)

        org.status_code = OrgStatus.INACTIVE.value
        org.save()

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
    def get_login_options_for_org(org_id, token_info: Dict = None, allowed_roles: Tuple = None):
        """Get the payment settings for the given org."""
        current_app.logger.debug('get_login_options(>')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Check authorization for the user
        check_auth(token_info, one_of_roles=allowed_roles, org_id=org_id)
        return AccountLoginOptionsModel.find_active_by_org_id(org_id)

    @staticmethod
    def add_login_option(org_id, login_source, token_info: Dict = None):
        """Create a new contact for this org."""
        # check for existing contact (only one contact per org for now)
        current_app.logger.debug('>add_login_option')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        check_auth(token_info, one_of_roles=ADMIN, org_id=org_id)

        login_option = AccountLoginOptionsModel(login_source=login_source, org_id=org_id)
        login_option.save()
        return login_option

    @staticmethod
    def update_login_option(org_id, login_source, token_info: Dict = None):
        """Create a new contact for this org."""
        # check for existing contact (only one contact per org for now)
        current_app.logger.debug('>update_login_option')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        check_auth(token_info, one_of_roles=(ADMIN, STAFF), org_id=org_id)

        existing_login_option = AccountLoginOptionsModel.find_active_by_org_id(org_id)
        if existing_login_option is not None:
            existing_login_option.is_active = False
            existing_login_option.add_to_session()

        login_option = AccountLoginOptionsModel(login_source=login_source, org_id=org_id)
        login_option.save()
        return login_option

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

        contact_link = ContactLinkModel()
        contact_link.contact = contact
        contact_link.org = org
        contact_link.save()
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
        contact.save()
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
        return len([x for x in self._model.members if x.membership_type_code == ADMIN])

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
        else:
            include_invitations: bool = False

            page: int = int(kwargs.get('page'))
            limit: int = int(kwargs.get('limit'))
            status: str = kwargs.get('status', None)
            name: str = kwargs.get('name', None)

            search_args = (kwargs.get('access_type', None),
                           name,
                           status,
                           kwargs.get('bcol_account_id', None),
                           page, limit)

            if status and status == OrgStatus.PENDING_ACTIVATION.value:
                org_models, total = OrgModel.search_pending_activation_orgs(name)
                include_invitations = True
            else:
                org_models, total = OrgModel.search_org(*search_args)

            for org in org_models:
                org_dict = Org(org).as_dict()
                org_dict['contacts'] = []
                org_dict['invitations'] = []

                if org.contacts:
                    org_dict['contacts'].append(
                        ContactSchema(exclude=('links',)).dump(org.contacts[0].contact, many=False))

                if include_invitations and org.invitations:
                    org_dict['invitations'].append(
                        InvitationSchema(exclude=('membership',)).dump(org.invitations[0].invitation, many=False))

                orgs['orgs'].append(org_dict)

            orgs['total'] = total
            orgs['page'] = page
            orgs['limit'] = limit

        return orgs

    @staticmethod
    def bcol_account_link_check(bcol_account_id, org_id=None):
        """Validate the BCOL id is linked or not. If already linked, return True."""
        if current_app.config.get('BCOL_ACCOUNT_LINK_CHECK'):
            account_payment = AccountPaymentModel.find_by_bcol_account_id(bcol_account_id, org_id)
            if account_payment:
                return True

        return False

    @staticmethod
    def approve_or_reject(org_id: int, is_approved: bool, token_info: Dict, origin_url: str = None):
        """Mark the affidavit as approved or rejected."""
        current_app.logger.debug('<find_affidavit_by_org_id ')
        # Get the org and check what's the current status
        org: OrgModel = OrgModel.find_by_org_id(org_id)

        # Current User
        user: UserModel = UserModel.find_by_jwt_token(token=token_info)

        # If status is PENDING_AFFIDAVIT_REVIEW handle affidavit approve process, else raise error
        if org.status_code == OrgStatus.PENDING_AFFIDAVIT_REVIEW.value:
            AffidavitService.approve_or_reject(org_id, is_approved, user)
        else:
            raise BusinessException(Error.INVALID_INPUT, None)

        if is_approved:
            org.status_code = OrgStatus.ACTIVE.value
        else:
            org.status_code = OrgStatus.REJECTED.value

        org.decision_made_by = user.username
        org.decision_made_on = datetime.now()

        # TODO Publish to activity stream

        org.save()

        # Find admin email address
        admin_email = ContactLinkModel.find_by_user_id(org.members[0].user.id).contact.email
        Org.send_approved_rejected_notification(admin_email, org.name, org.status_code, origin_url)

        current_app.logger.debug('>find_affidavit_by_org_id ')
        return Org(org)

    @staticmethod
    def send_staff_review_account_reminder(user, org_id, origin_url):
        """Send staff review account reminder notification."""
        current_app.logger.debug('<send_staff_review_account_reminder')
        subject = '[BC Registries & Online Services] An out of province account needs to be approved.'
        sender = current_app.config.get('MAIL_FROM_ID')
        recipient = current_app.config.get('STAFF_ADMIN_EMAIL')
        template = ENV.get_template('email_templates/staff_review_account_email.html')
        context_path = f'review-account/{org_id}'
        app_url = '{}/{}'.format(origin_url, current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH'))
        review_url = '{}/{}'.format(app_url, context_path)
        logo_url = f'{app_url}/{current_app.config.get("REGISTRIES_LOGO_IMAGE_NAME")}'

        try:
            sent_response = send_email(subject, sender, recipient,
                                       template.render(url=review_url, user=user, logo_url=logo_url))
            current_app.logger.debug('<send_staff_review_account_reminder')
            if not sent_response:
                current_app.logger.error('<send_staff_review_account_reminder failed')
                raise BusinessException(Error.FAILED_NOTIFICATION, None)
        except:  # noqa=B901
            current_app.logger.error('<send_staff_review_account_reminder failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None)

    @staticmethod
    def send_approved_rejected_notification(receipt_admin_email, org_name, org_status: OrgStatus, origin_url):
        """Send Approved/Rejected notification to the user."""
        current_app.logger.debug('<send_approved_rejected_notification')
        sender = current_app.config.get('MAIL_FROM_ID')
        if org_status == OrgStatus.ACTIVE.value:
            template = ENV.get_template('email_templates/nonbcsc_org_approved_notification_email.html')
            subject = '[BC Registries & Online Services] APPROVED Business Registry Account'
        elif org_status == OrgStatus.REJECTED.value:
            template = ENV.get_template('email_templates/nonbcsc_org_rejected_notification_email.html')
            subject = '[BC Registries & Online Services] YOUR ACTION REQUIRED: ' \
                      'Business Registry Account cannot be approved'
        else:
            return  # dont send mail for any other status change
        app_url = '{}/{}'.format(origin_url, current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH'))
        logo_url = f'{app_url}/{current_app.config.get("REGISTRIES_LOGO_IMAGE_NAME")}'
        params = {'org_name': org_name}
        try:
            sent_response = send_email(subject, sender, receipt_admin_email,
                                       template.render(url=app_url, params=params, org_name=org_name,
                                                       logo_url=logo_url))
            current_app.logger.debug('<send_approved_rejected_notification')
            if not sent_response:
                current_app.logger.error('<send_approved_rejected_notification failed')
                raise BusinessException(Error.FAILED_NOTIFICATION, None)
        except:  # noqa=B901
            current_app.logger.error('<send_approved_rejected_notification failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None)

    @staticmethod
    def add_product(org_id, token_info: Dict = None):
        """Add product subscription."""
        if token_info:
            # set as defalut type
            product_code = ProductCode.BUSINESS.value

            # Token is from service account, get the product code claim
            if Role.SYSTEM.value in token_info.get('realm_access').get('roles'):
                product_code = token_info.get('product_code', None)

            if product_code:
                product_subscription = {'subscriptions': [{'productCode': product_code}]}
                subscriptions = ProductService.create_product_subscription(org_id, product_subscription,
                                                                           is_new_transaction=False)
                return subscriptions
        return None
