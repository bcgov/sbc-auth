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
from datetime import datetime
from typing import Dict, Tuple

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import AccountLoginOptions as AccountLoginOptionsModel
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import User as UserModel
from auth_api.models.affidavit import Affidavit as AffidavitModel
from auth_api.schemas import ContactSchema, InvitationSchema, OrgSchema
from auth_api.services.validators.access_type import validate as access_type_validate
from auth_api.services.validators.account_limit import validate as account_limit_validate
from auth_api.services.validators.bcol_credentials import validate as bcol_credentials_validate
from auth_api.services.validators.duplicate_org_name import validate as duplicate_org_name_validate
from auth_api.utils.enums import (
    AccessType, ChangeType, OrgStatus, OrgType, PaymentAccountStatus, PaymentMethod, Status, TaskRelationshipStatus,
    TaskRelationshipType, TaskStatus, TaskTypePrefix)
from auth_api.utils.roles import ADMIN, EXCLUDED_FIELDS, STAFF, VALID_STATUSES, Role
from auth_api.utils.util import camelback2snake

from ..utils.account_mailer import publish_to_mailer
from ..utils.user_context import UserContext, user_context
from .affidavit import Affidavit as AffidavitService
from .authorization import check_auth
from .contact import Contact as ContactService
from .keycloak import KeycloakService
from .products import Product as ProductService
from .rest_service import RestService
from .task import Task as TaskService
from .validators.validator_response import ValidatorResponse

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
    @user_context
    def create_org(org_info: dict, user_id,  # pylint: disable=too-many-locals, too-many-statements, too-many-branches
                   origin_url: str = None, **kwargs):
        """Create a new organization."""
        current_app.logger.debug('<create_org ')
        # bcol is treated like an access type as well;so its outside the scheme
        mailing_address = org_info.pop('mailingAddress', None)
        payment_info = org_info.pop('paymentInfo', {})
        selected_payment_method = payment_info.get('paymentMethod', None)
        org_type = org_info.get('typeCode', OrgType.BASIC.value)
        bcol_profile_flags = None
        validate_response: ValidatorResponse = Org._validate_and_raise_error(org_info)
        # If the account is created using BCOL credential, verify its valid bc online account
        bcol_details_response = validate_response.response.get('bcol_response', None)
        if bcol_details_response is not None and (bcol_details := bcol_details_response.json()) is not None:
            Org._map_response_to_org(bcol_details, org_info)
            bcol_profile_flags = bcol_details.get('profileFlags')

        access_type = validate_response.response.get('access_type')

        # set premium for GOVM accounts..TODO remove if not needed this logic
        if access_type == AccessType.GOVM.value:
            org_type = OrgType.PREMIUM.value
            org_info.update({'typeCode': OrgType.PREMIUM.value})

        org = OrgModel.create_from_dict(camelback2snake(org_info))
        org.access_type = access_type
        # If the account is anonymous or govm set the billable value as False else True
        org.billable = access_type not in [AccessType.ANONYMOUS.value, AccessType.GOVM.value]
        # Set the status based on access type
        # Check if the user is APPROVED else set the org status to PENDING
        # Send an email to staff to remind review the pending account
        if access_type in (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value) \
                and not AffidavitModel.find_approved_by_user_id(user_id=user_id):
            Org._handle_bceid_status_and_notification(org, origin_url)

        if access_type == AccessType.GOVM.value:
            org.status_code = OrgStatus.PENDING_INVITE_ACCEPT.value

        # If mailing address is provided, save it
        if mailing_address:
            Org.add_contact_to_org(mailing_address, org)

        # create the membership record for this user if its not created by staff and access_type is anonymous
        Org.create_membership(access_type, org, user_id)

        # dir search and GOVM doesnt need default products
        if access_type not in (AccessType.ANONYMOUS.value, AccessType.GOVM.value):
            ProductService.create_default_product_subscriptions(org, bcol_profile_flags, is_new_transaction=False)

        payment_method = Org._validate_and_get_payment_method(selected_payment_method, OrgType[org_type],
                                                              access_type=access_type)

        user_name = ''
        if payment_method == PaymentMethod.PAD.value:  # to get the pad accepted date
            user_from_context: UserContext = kwargs['user']
            user: UserModel = UserModel.find_by_jwt_token(token=user_from_context.token_info)
            user_name = user.username

        Org._create_payment_settings(org, payment_info, payment_method, mailing_address, user_name, True)

        # TODO do we have to check anything like this below?
        # if payment_account_status == PaymentAccountStatus.FAILED:
        # raise BusinessException(Error.ACCOUNT_CREATION_FAILED_IN_PAY, None)

        org.commit()

        current_app.logger.info(f'<created_org org_id:{org.id}')

        return Org(org)

    @staticmethod
    @user_context
    def _handle_bceid_status_and_notification(org, origin_url, **kwargs):
        org.status_code = OrgStatus.PENDING_STAFF_REVIEW.value
        user_from_context: UserContext = kwargs['user']
        user = UserModel.find_by_jwt_token(token=user_from_context.token_info)
        # Org.send_staff_review_account_reminder(user, org.id, origin_url)
        # create a staff review task for this account
        task_type = TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
        task_info = {'name': org.name,
                     'relationshipId': org.id,
                     'relatedTo': user.id,
                     'dateSubmitted': datetime.today(),
                     'relationshipType': TaskRelationshipType.ORG.value,
                     'type': task_type,
                     'status': TaskStatus.OPEN.value,
                     'relationship_status': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
                     }
        TaskService.create_task(task_info=task_info, user=user, origin_url=origin_url, do_commit=False)

    @staticmethod
    def _validate_and_get_payment_method(selected_payment_type: str, org_type: OrgType, access_type=None) -> str:

        # TODO whats a  better place for this
        org_payment_method_mapping = {
            OrgType.BASIC: (
                PaymentMethod.CREDIT_CARD.value, PaymentMethod.DIRECT_PAY.value, PaymentMethod.ONLINE_BANKING.value),
            OrgType.PREMIUM: (
                PaymentMethod.CREDIT_CARD.value, PaymentMethod.DIRECT_PAY.value,
                PaymentMethod.PAD.value, PaymentMethod.BCOL.value)
        }
        if access_type == AccessType.GOVM.value:
            payment_type = PaymentMethod.EJV.value
        elif selected_payment_type:
            valid_types = org_payment_method_mapping.get(org_type, [])
            if selected_payment_type in valid_types:
                payment_type = selected_payment_type
            else:
                raise BusinessException(Error.INVALID_INPUT, None)
        else:
            payment_type = PaymentMethod.BCOL.value if \
                org_type == OrgType.PREMIUM else Org._get_default_payment_method_for_creditcard()
        return payment_type

    @staticmethod
    @user_context
    def create_membership(access_type, org, user_id, **kwargs):
        """Create membership account."""
        user: UserContext = kwargs['user']
        if not user.is_staff_admin() and access_type != AccessType.ANONYMOUS.value:
            membership = MembershipModel(org_id=org.id, user_id=user_id, membership_type_code='ADMIN',
                                         membership_type_status=Status.ACTIVE.value)
            membership.add_to_session()

            # Add the user to account_holders group
            KeycloakService.join_account_holders_group()

    @staticmethod
    def _validate_account_limit(is_staff_admin, user_id):
        """Validate account limit."""
        if not is_staff_admin:  # staff can create any number of orgs
            count = OrgModel.get_count_of_org_created_by_user_id(user_id)
            if count >= current_app.config.get('MAX_NUMBER_OF_ORGS'):
                raise BusinessException(Error.MAX_NUMBER_OF_ORGS_LIMIT, None)

    @staticmethod
    def _create_payment_settings(org_model: OrgModel, payment_info: dict,  # pylint: disable=too-many-arguments
                                 payment_method: str, mailing_address=None, username: str = None,
                                 is_new_org: bool = True) -> PaymentAccountStatus:
        """Add payment settings for the org."""
        pay_url = current_app.config.get('PAY_API_URL')
        org_name_for_pay = f'{org_model.name}-{org_model.branch_name}' if org_model.branch_name else org_model.name
        pay_request = {
            'accountId': org_model.id,
            # pay needs the most unique idenitfier.So combine name and branch name
            'accountName': org_name_for_pay,
            'paymentInfo': {
                'methodOfPayment': payment_method,
                'billable': org_model.billable
            }
        }
        if mailing_address:
            pay_request['contactInfo'] = mailing_address

        if org_model.bcol_account_id:
            pay_request['bcolAccountNumber'] = org_model.bcol_account_id
            pay_request['bcolUserId'] = org_model.bcol_user_id

        if (revenue_account := payment_info.get('revenueAccount')) is not None:
            pay_request['paymentInfo']['revenueAccount'] = revenue_account

        if payment_method == PaymentMethod.PAD.value:  # PAD has bank related details
            pay_request['paymentInfo']['bankTransitNumber'] = payment_info.get('bankTransitNumber', None)
            pay_request['paymentInfo']['bankInstitutionNumber'] = payment_info.get('bankInstitutionNumber', None)
            pay_request['paymentInfo']['bankAccountNumber'] = payment_info.get('bankAccountNumber', None)
            pay_request['padTosAcceptedBy'] = username
        # invoke pay-api
        token = RestService.get_service_account_token()
        if is_new_org:
            response = RestService.post(endpoint=f'{pay_url}/accounts',
                                        data=pay_request, token=token, raise_for_status=True)
        else:
            response = RestService.put(endpoint=f'{pay_url}/accounts/{org_model.id}',
                                       data=pay_request, token=token, raise_for_status=True)

        if response == http_status.HTTP_200_OK:
            payment_account_status = PaymentAccountStatus.CREATED
        elif response == http_status.HTTP_202_ACCEPTED:
            payment_account_status = PaymentAccountStatus.PENDING
        else:
            payment_account_status = PaymentAccountStatus.FAILED

        return payment_account_status

    @staticmethod
    def _validate_and_raise_error(org_info: dict):
        """Execute the validators in chain and raise error or return."""
        validators = [account_limit_validate, access_type_validate, duplicate_org_name_validate]
        access_type: str = org_info.get('accessType', None)
        arg_dict = {'accessType': access_type,
                    'name': org_info.get('name'),
                    'branch_name': org_info.get('branchName')}
        if (bcol_credential := org_info.pop('bcOnlineCredential', None)) is not None:
            validators.insert(0, bcol_credentials_validate)
            arg_dict['bcol_credential'] = bcol_credential
        validator_response = ValidatorResponse()

        for validator in validators:
            validator(validator_response, **arg_dict)

        if not validator_response.is_valid:
            raise BusinessException(validator_response.error[0], None)
        return validator_response

    @staticmethod
    def _get_default_payment_method_for_creditcard():
        return PaymentMethod.DIRECT_PAY.value if current_app.config.get(
            'DIRECT_PAY_ENABLED') else PaymentMethod.CREDIT_CARD.value

    @staticmethod
    def get_bcol_details(bcol_credential: Dict, org_id=None):
        """Retrieve and validate BC Online credentials."""
        validator_obj = ValidatorResponse()
        arg_dict = {'bcol_credential': bcol_credential,
                    'org_id': org_id}
        bcol_credentials_validate(validator_obj, **arg_dict)
        if not validator_obj.is_valid:
            raise BusinessException(validator_obj.error[0], None)
        return validator_obj.response.get('bcol_response', None)

    def change_org_ype(self, org_info, action=None):
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
            # TODO fix this
            # if org_info.get('name') != self._model.name:
            # Org.raise_error_if_duplicate_name(org_info['name'])

            # remove the bcol payment details from payment table
            org_info['bcol_account_id'] = ''
            org_info['bcol_user_id'] = ''
            org_info['bcol_account_name'] = ''
            payment_type = Org._get_default_payment_method_for_creditcard()
            # TODO Add the pay-api call here
            Org.__delete_contact(self._model)

        if action == ChangeType.UPGRADE.value:
            if org_info.get('typeCode') != OrgType.PREMIUM.value or bcol_credential is None:
                raise BusinessException(Error.INVALID_INPUT, None)
            bcol_response = Org.get_bcol_details(bcol_credential, self._model.id).json()
            Org._map_response_to_org(bcol_response, org_info)
            ProductService.create_subscription_from_bcol_profile(self._model.id, bcol_response.get('profileFlags'))
            payment_type = PaymentMethod.BCOL.value

            # If mailing address is provided, save it
            if mailing_address:
                self.add_contact_to_org(mailing_address, self._model)

        self._model.update_org_from_dict(camelback2snake(org_info), exclude=('status_code'))
        # TODO pass username instead of blanks
        Org._create_payment_settings(self._model, {}, payment_type, mailing_address, '', False)
        return self

    @staticmethod
    def _map_response_to_org(bcol_response, org_info):
        org_info.update({
            'bcol_account_id': bcol_response.get('accountNumber'),
            'bcol_user_id': bcol_response.get('userId'),
            'bcol_account_name': bcol_response.get('orgName')
        })

        # New org who linked to BCOL account will use BCOL account name as default name
        # Existing account keep their account name to avoid payment info change.
        if not org_info.get('name'):
            org_info.update({'name': bcol_response.get('orgName')})

    @staticmethod
    def add_contact_to_org(mailing_address, org):
        """Update the passed organization with the mailing address."""
        contact = ContactModel(**camelback2snake(mailing_address))
        contact = contact.add_to_session()
        contact_link = ContactLinkModel()
        contact_link.contact = contact
        contact_link.org = org
        contact_link.add_to_session()

    @staticmethod
    def raise_error_if_duplicate_name(name, branch_name=None):
        """Raise error if there is duplicate org name already."""
        validator_obj = ValidatorResponse()
        arg_dict = {'name': name,
                    'branch_name': branch_name}
        duplicate_org_name_validate(validator_obj, **arg_dict)
        if not validator_obj.is_valid:
            raise BusinessException(validator_obj.error[0], None)

    def update_org(self, org_info, token_info: Dict = None,  # pylint: disable=too-many-locals
                   origin_url: str = None):
        """Update the passed organization with the new info."""
        current_app.logger.debug('<update_org ')

        has_org_updates: bool = False  # update the org table if this variable is set true
        has_status_changing: bool = False

        org_model: OrgModel = self._model
        # to enforce necessary details for govm account creation
        is_govm_account = org_model.access_type == AccessType.GOVM.value
        is_govm_account_creation = \
            is_govm_account and org_model.status_code == OrgStatus.PENDING_INVITE_ACCEPT.value

        # govm name is not being updated now
        is_name_getting_updated = 'name' in org_info and not is_govm_account
        if is_name_getting_updated:
            existing_similar__org = OrgModel.find_similar_org_by_name(org_info['name'], self._model.id)
            if existing_similar__org is not None:
                raise BusinessException(Error.DATA_CONFLICT, None)
            has_org_updates = True

        # If the account is created using BCOL credential, verify its valid bc online account
        # If it's a valid account disable the current one and add a new one
        if bcol_credential := org_info.pop('bcOnlineCredential', None):
            bcol_response = Org.get_bcol_details(bcol_credential, self._model.id).json()
            Org._map_response_to_org(bcol_response, org_info)
            ProductService.create_subscription_from_bcol_profile(org_model.id, bcol_response.get('profileFlags'))
            has_org_updates = True

        product_subscriptions = org_info.pop('productSubscriptions', None)
        mailing_address = org_info.pop('mailingAddress', None)
        payment_info = org_info.pop('paymentInfo', {})
        if is_govm_account_creation and (mailing_address is None or payment_info.get('revenueAccount') is None):
            raise BusinessException(Error.GOVM_ACCOUNT_DATA_MISSING, None)

        if is_govm_account_creation:
            has_org_updates = True
            org_info['statusCode'] = OrgStatus.PENDING_STAFF_REVIEW.value
            has_status_changing = True
            self._create_gov_account_task(org_model, token_info, origin_url)
        if product_subscriptions is not None:
            subscription_data = {'subscriptions': product_subscriptions}
            ProductService.create_product_subscription(self._model.id, subscription_data=subscription_data,
                                                       skip_auth=True, token_info=token_info)

        # Update mailing address Or create new one
        if mailing_address:
            contacts = self._model.contacts
            if len(contacts) > 0:
                contact = self._model.contacts[0].contact
                contact.update_from_dict(**camelback2snake(mailing_address))
                contact.save()
            else:
                Org.add_contact_to_org(mailing_address, self._model)

        if has_org_updates:
            excluded = ('type_code',) if has_status_changing else EXCLUDED_FIELDS
            self._model.update_org_from_dict(camelback2snake(org_info), exclude=excluded)

        if payment_info:
            selected_payment_method = payment_info.get('paymentMethod', None)
            payment_type = Org._validate_and_get_payment_method(selected_payment_method, OrgType[self._model.type_code],
                                                                self._model.access_type)
            user: UserModel = UserModel.find_by_jwt_token(token=token_info)
            # TODO when updating the bank info , dont pass user.username as tos updated by..handle this
            Org._create_payment_settings(self._model, payment_info, payment_type, mailing_address, user.username, False)
            current_app.logger.debug('>update_org ')
        return self

    @staticmethod
    def _create_gov_account_task(org_model: OrgModel, token_info: dict, origin_url: str):
        # create a staff review task for this account
        task_type = TaskTypePrefix.GOVM_REVIEW.value
        user: UserModel = UserModel.find_by_jwt_token(token=token_info)
        task_info = {'name': org_model.name,
                     'relationshipId': org_model.id,
                     'relatedTo': user.id,
                     'dateSubmitted': datetime.today(),
                     'relationshipType': TaskRelationshipType.ORG.value,
                     'type': task_type,
                     'status': TaskStatus.OPEN.value,
                     'relationship_status': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
                     }
        TaskService.create_task(task_info=task_info, user=user, do_commit=False, origin_url=origin_url)

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

        # Don't remove account if it's staff who deactivate org.
        is_staff_admin = token_info and Role.STAFF_CREATE_ACCOUNTS.value in token_info.get('realm_access').get('roles')
        if not is_staff_admin:
            # Remove user from thr group if the user doesn't have any other orgs membership
            user = UserModel.find_by_jwt_token(token=token_info)
            if len(MembershipModel.find_orgs_for_user(user.id)) == 0:
                KeycloakService.remove_from_account_holders_group(user.keycloak_guid)

        current_app.logger.debug('org Inactivated>')

    def get_payment_info(self):
        """Return the Payment Details for an org by calling Pay API."""
        pay_url = current_app.config.get('PAY_API_URL')
        # invoke pay-api
        token = RestService.get_service_account_token()
        response = RestService.get(endpoint=f'{pay_url}/accounts/{self._model.id}', token=token, retry_on_failure=True)
        return response.json()

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
    def find_by_org_name(org_name):
        """Find and return an existing organization with the provided name."""
        if org_name is None:
            return None

        org_model = OrgModel.find_by_org_name(org_name)
        if not org_model:
            return None

        orgs = {'orgs': []}

        for org in org_model:
            orgs['orgs'].append(Org(org).as_dict())

        return orgs

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

        check_auth(token_info, one_of_roles=ADMIN, org_id=org_id)

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
    def search_orgs(**kwargs):  # pylint: disable=too-many-locals
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
            statuses: str = kwargs.get('statuses', None)
            name: str = kwargs.get('name', None)
            # https://github.com/bcgov/entity/issues/4786
            access_type, is_staff_admin = Org.refine_access_type(kwargs.get('access_type', None),
                                                                 kwargs.get('token', None))
            search_args = (access_type,
                           name,
                           statuses,
                           kwargs.get('bcol_account_id', None),
                           page, limit)

            if statuses and OrgStatus.PENDING_ACTIVATION.value in statuses:
                # only staff admin can see director search accounts
                # https://github.com/bcgov/entity/issues/4786
                if not is_staff_admin:
                    raise BusinessException(Error.INVALID_USER_CREDENTIALS, None)
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
    def refine_access_type(access_type_str, token_info):
        """Find Access Type."""
        roles = token_info.get('realm_access').get('roles')

        is_staff_admin = token_info and (Role.STAFF_CREATE_ACCOUNTS.value in roles or
                                         Role.STAFF_MANAGE_ACCOUNTS.value in roles)
        access_type = [] if not access_type_str else access_type_str.split(',')
        if not is_staff_admin:
            if len(access_type) < 1:
                # pass everything except DIRECTOR SEARCH
                access_type = [item.value for item in AccessType if item != AccessType.ANONYMOUS]
            else:
                access_type.remove(AccessType.ANONYMOUS.value)
        return access_type, is_staff_admin

    @staticmethod
    def bcol_account_link_check(bcol_account_id, org_id=None):
        """Validate the BCOL id is linked or not. If already linked, return True."""
        if current_app.config.get('BCOL_ACCOUNT_LINK_CHECK'):
            org = OrgModel.find_by_bcol_id(bcol_account_id)
            if org and org.id != org_id:  # check if already taken up by different org
                return True

        return False

    @staticmethod
    def change_org_status(org_id: int, status_code, suspension_reason_code, token_info: Dict = None):
        """Update the status of the org.

        Used now for suspending/activate account.

            1) check access .only staff can do it now
            2) check org status/eligiblity
            3) suspend it

        """
        current_app.logger.debug('<change_org_status ')

        org_model: OrgModel = OrgModel.find_by_org_id(org_id)

        user: UserModel = UserModel.find_by_jwt_token(token=token_info)
        current_app.logger.debug('<setting org status to  ')
        org_model.status_code = status_code
        org_model.decision_made_by = user.username  # not sure if a new field is needed for this.
        if status_code == OrgStatus.SUSPENDED.value:
            org_model.suspended_on = datetime.today()
            org_model.suspension_reason_code = suspension_reason_code
        org_model.save()
        current_app.logger.debug('change_org_status>')
        return Org(org_model)

    @staticmethod
    def approve_or_reject(org_id: int, is_approved: bool, token_info: Dict, origin_url: str = None):
        """Mark the affidavit as approved or rejected."""
        current_app.logger.debug('<find_affidavit_by_org_id ')
        # Get the org and check what's the current status
        org: OrgModel = OrgModel.find_by_org_id(org_id)

        # Current User
        user: UserModel = UserModel.find_by_jwt_token(token=token_info)

        # If status is PENDING_STAFF_REVIEW handle affidavit approve process, else raise error
        if org.status_code == OrgStatus.PENDING_STAFF_REVIEW.value and \
                org.access_type in (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value):
            AffidavitService.approve_or_reject(org_id, is_approved, user)
        elif org.status_code != OrgStatus.PENDING_STAFF_REVIEW.value or \
                org.access_type not in \
                (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value, AccessType.GOVM.value):
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
        if org.access_type in (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value):
            Org.send_approved_rejected_notification(admin_email, org.name, org.id, org.status_code, origin_url)
        elif org.access_type == AccessType.GOVM.value:
            Org.send_approved_govm_notification(admin_email, org.id, org.status_code, origin_url)

        current_app.logger.debug('>find_affidavit_by_org_id ')
        return Org(org)

    @staticmethod
    def send_staff_review_account_reminder(user, org_id, origin_url):
        """Send staff review account reminder notification."""
        current_app.logger.debug('<send_staff_review_account_reminder')
        recipient = current_app.config.get('STAFF_ADMIN_EMAIL')
        context_path = f'review-account/{org_id}'
        app_url = '{}/{}'.format(origin_url, current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH'))
        review_url = '{}/{}'.format(app_url, context_path)
        first_name = ''
        last_name = ''

        if user:
            first_name = user.firstname
            last_name = user.lastname

        data = {
            'accountId': org_id,
            'emailAddresses': recipient,
            'contextUrl': review_url,
            'userFirstName': first_name,
            'userLastName': last_name
        }
        try:
            publish_to_mailer('staffReviewAccount', org_id=org_id, data=data)
            current_app.logger.debug('<send_staff_review_account_reminder')
        except:  # noqa=B901
            current_app.logger.error('<send_staff_review_account_reminder failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None)

    @staticmethod
    def send_approved_rejected_notification(receipt_admin_email, org_name, org_id, org_status: OrgStatus, origin_url):
        """Send Approved/Rejected notification to the user."""
        current_app.logger.debug('<send_approved_rejected_notification')

        if org_status == OrgStatus.ACTIVE.value:
            notification_type = 'nonbcscOrgApprovedNotification'
        elif org_status == OrgStatus.REJECTED.value:
            notification_type = 'nonbcscOrgRejectedNotification'
        else:
            return  # dont send mail for any other status change
        app_url = '{}/{}'.format(origin_url, current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH'))
        data = {
            'accountId': org_id,
            'emailAddresses': receipt_admin_email,
            'contextUrl': app_url,
            'org_name': org_name
        }
        try:
            publish_to_mailer(notification_type, org_id=org_id, data=data)
            current_app.logger.debug('<send_approved_rejected_notification')
        except:  # noqa=B901
            current_app.logger.error('<send_approved_rejected_notification failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None)

    @staticmethod
    def send_approved_govm_notification(receipt_admin_email, org_id, org_status: OrgStatus, origin_url):
        """Send Approved govm notification to the user."""
        current_app.logger.debug('<send_approved_govm_notification')

        if org_status == OrgStatus.ACTIVE.value:
            notification_type = 'govmApprovedNotification'
        else:
            return  # dont send mail for any other status change
        app_url = '{}/{}'.format(origin_url, current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH'))
        data = {
            'accountId': org_id,
            'emailAddresses': receipt_admin_email,
            'contextUrl': app_url,
        }
        try:
            publish_to_mailer(notification_type, org_id=org_id, data=data)
            current_app.logger.debug('send_approved_govm_notification>')
        except:  # noqa=B901
            current_app.logger.error('<send_approved_govm_notification failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None)
