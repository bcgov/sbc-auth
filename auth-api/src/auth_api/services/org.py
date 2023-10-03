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
import json
from typing import Dict, List, Tuple

from flask import current_app, g
from jinja2 import Environment, FileSystemLoader
from requests.exceptions import HTTPError
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api import status as http_status
from auth_api.models.dataclass import Activity, DeleteAffiliationRequest, PaginationInfo
from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import AccountLoginOptions as AccountLoginOptionsModel
from auth_api.models import Contact as ContactModel
from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models import Membership as MembershipModel
from auth_api.models import Org as OrgModel
from auth_api.models import User as UserModel
from auth_api.models import Task as TaskModel
from auth_api.models.affidavit import Affidavit as AffidavitModel
from auth_api.models.org import OrgSearch
from auth_api.schemas import ContactSchema, InvitationSchema, OrgSchema
from auth_api.services.user import User as UserService
from auth_api.services.validators.access_type import validate as access_type_validate
from auth_api.services.validators.account_limit import validate as account_limit_validate
from auth_api.services.validators.bcol_credentials import validate as bcol_credentials_validate
from auth_api.services.validators.duplicate_org_name import validate as duplicate_org_name_validate
from auth_api.services.validators.payment_type import validate as payment_type_validate
from auth_api.utils.enums import (
    AccessType, ActivityAction, AffidavitStatus, LoginSource, OrgStatus, OrgType, PatchActions, PaymentAccountStatus,
    PaymentMethod, Status, SuspensionReasonCode, TaskRelationshipStatus, TaskRelationshipType, TaskStatus,
    TaskTypePrefix, TaskAction)
from auth_api.utils.roles import ADMIN, EXCLUDED_FIELDS, STAFF, VALID_STATUSES, Role  # noqa: I005
from auth_api.utils.util import camelback2snake

from ..utils.account_mailer import publish_to_mailer
from ..utils.user_context import UserContext, user_context
from .activity_log_publisher import ActivityLogPublisher
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
    def create_org(org_info: dict, user_id):
        """Create a new organization."""
        current_app.logger.debug('<create_org ')
        # bcol is treated like an access type as well;so its outside the scheme
        mailing_address = org_info.pop('mailingAddress', None)
        payment_info = org_info.pop('paymentInfo', {})
        product_subscriptions = org_info.pop('productSubscriptions', None)

        bcol_profile_flags = None
        response = Org._validate_and_raise_error(org_info)
        # If the account is created using BCOL credential, verify its valid bc online account
        bcol_details_response = response.get('bcol_response', None)
        if bcol_details_response is not None and (bcol_details := bcol_details_response.json()) is not None:
            Org._map_response_to_org(bcol_details, org_info)
            bcol_profile_flags = bcol_details.get('profileFlags')

        access_type = response.get('access_type')

        # set premium for GOVM accounts..TODO remove if not needed this logic
        if access_type == AccessType.GOVM.value:
            org_info.update({'typeCode': OrgType.PREMIUM.value})

        org = OrgModel.create_from_dict(camelback2snake(org_info))
        org.access_type = access_type

        # Set the status based on access type
        # Check if the user is APPROVED else set the org status to PENDING

        if access_type == AccessType.GOVM.value:
            org.status_code = OrgStatus.PENDING_INVITE_ACCEPT.value

        # If mailing address is provided, save it
        if mailing_address:
            Org.add_contact_to_org(mailing_address, org)

        # create the membership record for this user if its not created by staff and access_type is anonymous
        Org.create_membership(access_type, org, user_id)

        if product_subscriptions is not None:
            subscription_data = {'subscriptions': product_subscriptions}
            ProductService.create_product_subscription(org.id, subscription_data=subscription_data,
                                                       skip_auth=True)

        ProductService.create_subscription_from_bcol_profile(org.id, bcol_profile_flags)

        Org._create_payment_for_org(mailing_address, org, payment_info, True)

        # TODO do we have to check anything like this below?
        # if payment_account_status == PaymentAccountStatus.FAILED:
        # raise BusinessException(Error.ACCOUNT_CREATION_FAILED_IN_PAY, None)

        # Send an email to staff to remind review the pending account
        is_staff_review_needed = access_type in (
            AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value, AccessType.GOVN.value
        ) and not AffidavitModel.find_approved_by_user_id(user_id=user_id)

        user = UserModel.find_by_jwt_token()
        if is_staff_review_needed:
            Org._create_staff_review_task(org, user)

        org.commit()

        ProductService.update_org_product_keycloak_groups(org.id)

        current_app.logger.info(f'<created_org org_id:{org.id}')

        return Org(org)

    @staticmethod
    def _create_staff_review_task(org: OrgModel, user: UserModel):
        org.status_code = OrgStatus.PENDING_STAFF_REVIEW.value
        # create a staff review task for this account
        task_type = TaskTypePrefix.GOVN_REVIEW.value if org.access_type == AccessType.GOVN.value \
            else TaskTypePrefix.NEW_ACCOUNT_STAFF_REVIEW.value
        action = TaskAction.AFFIDAVIT_REVIEW.value if user.login_source == LoginSource.BCEID.value \
            else TaskAction.ACCOUNT_REVIEW.value

        task_info = {
            'name': org.name,
            'relationshipId': org.id,
            'relatedTo': user.id,
            'dateSubmitted': datetime.today(),
            'relationshipType': TaskRelationshipType.ORG.value,
            'type': task_type,
            'action': action,
            'status': TaskStatus.OPEN.value,
            'relationship_status': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
        }
        TaskService.create_task(task_info=task_info, do_commit=False)
        Org.send_staff_review_account_reminder(relationship_id=org.id)

    @staticmethod
    @user_context
    def create_membership(access_type, org, user_id, **kwargs):
        """Create membership account."""
        user: UserContext = kwargs['user_context']
        if not user.is_staff_admin() and access_type != AccessType.ANONYMOUS.value:
            membership = MembershipModel(org_id=org.id, user_id=user_id, membership_type_code='ADMIN',
                                         membership_type_status=Status.ACTIVE.value)
            membership.add_to_session()

            # Add the user to account_holders group
            KeycloakService.join_account_holders_group()

    @staticmethod
    @user_context
    def _create_payment_settings(org_model: OrgModel, payment_info: dict,  # pylint: disable=too-many-arguments
                                 payment_method: str, mailing_address=None,
                                 is_new_org: bool = True, **kwargs):
        """Add payment settings for the org."""
        pay_url = current_app.config.get('PAY_API_URL')
        org_name_for_pay = f'{org_model.name}-{org_model.branch_name}' if org_model.branch_name else org_model.name
        pay_request = {
            'accountId': org_model.id,
            # pay needs the most unique idenitfier.So combine name and branch name
            'accountName': org_name_for_pay
        }

        if payment_method:
            pay_request['paymentInfo'] = {'methodOfPayment': payment_method}

        if mailing_address:
            pay_request['contactInfo'] = mailing_address

        if payment_method and org_model.bcol_account_id:
            pay_request['bcolAccountNumber'] = org_model.bcol_account_id
            pay_request['bcolUserId'] = org_model.bcol_user_id

        if (revenue_account := payment_info.get('revenueAccount')) is not None:
            pay_request.setdefault('paymentInfo', {})
            pay_request['paymentInfo']['revenueAccount'] = revenue_account

        if payment_method == PaymentMethod.PAD.value:  # PAD has bank related details
            pay_request['paymentInfo']['bankTransitNumber'] = payment_info.get('bankTransitNumber', None)
            pay_request['paymentInfo']['bankInstitutionNumber'] = payment_info.get('bankInstitutionNumber', None)
            pay_request['paymentInfo']['bankAccountNumber'] = payment_info.get('bankAccountNumber', None)
            pay_request['padTosAcceptedBy'] = kwargs['user_context'].user_name
        # invoke pay-api
        token = RestService.get_service_account_token()
        if is_new_org:
            response = RestService.post(endpoint=f'{pay_url}/accounts',
                                        data=pay_request, token=token, raise_for_status=True)
        else:
            response = RestService.put(endpoint=f'{pay_url}/accounts/{org_model.id}',
                                       data=pay_request, token=token, raise_for_status=True)

        if response.status_code == http_status.HTTP_200_OK:
            payment_account_status = PaymentAccountStatus.CREATED
        elif response.status_code == http_status.HTTP_202_ACCEPTED:
            payment_account_status = PaymentAccountStatus.PENDING
        else:
            payment_account_status = PaymentAccountStatus.FAILED

        if payment_account_status != PaymentAccountStatus.FAILED and payment_method:
            payment_method_description = PaymentMethod(payment_method).name if payment_method in [
                item.value for item in PaymentMethod] else ''
            ActivityLogPublisher.publish_activity(Activity(org_model.id, ActivityAction.PAYMENT_INFO_CHANGE.value,
                                                           name=org_model.name,
                                                           value=payment_method_description))
        return payment_account_status

    @staticmethod
    def _validate_and_raise_error(org_info: dict):
        """Execute the validators in chain and raise error or return."""
        validators = [account_limit_validate, access_type_validate, duplicate_org_name_validate]
        arg_dict = {'accessType': org_info.get('accessType', None),
                    'name': org_info.get('name'),
                    'branch_name': org_info.get('branchName')}
        if (bcol_credential := org_info.pop('bcOnlineCredential', None)) is not None:
            validators.insert(0, bcol_credentials_validate)  # first validator should be bcol ,thus 0th position
            arg_dict['bcol_credential'] = bcol_credential

        validator_response_list: List[ValidatorResponse] = []
        for validate in validators:
            validator_response_list.append(validate(**arg_dict))

        not_valid_obj = next((x for x in validator_response_list if getattr(x, 'is_valid', None) is False), None)
        if not_valid_obj:
            raise BusinessException(not_valid_obj.error[0], None)

        response: dict = {}
        for val in validator_response_list:
            response.update(val.info)
        return response

    @staticmethod
    def _get_default_payment_method_for_creditcard():
        return PaymentMethod.DIRECT_PAY.value if current_app.config.get(
            'DIRECT_PAY_ENABLED') else PaymentMethod.CREDIT_CARD.value

    @staticmethod
    def get_bcol_details(bcol_credential: Dict, org_id=None):
        """Retrieve and validate BC Online credentials."""
        arg_dict = {'bcol_credential': bcol_credential,
                    'org_id': org_id}
        validator_obj = bcol_credentials_validate(**arg_dict)
        if not validator_obj.is_valid:
            raise BusinessException(validator_obj.error[0], None)
        return validator_obj.info.get('bcol_response', None)

    @staticmethod
    def _map_response_to_org(bcol_response, org_info, do_link_name=True):
        org_info.update({
            'bcol_account_id': bcol_response.get('accountNumber'),
            'bcol_user_id': bcol_response.get('userId'),
        })

        if do_link_name:
            org_info.update({
                'bcol_account_name': bcol_response.get('orgName')
            })

        # New org who linked to BCOL account will use BCOL account name as default name
        # Existing account keep their account name to avoid payment info change.
        if not org_info.get('name') and do_link_name:
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

    def update_org(self, org_info):  # pylint: disable=too-many-locals, too-many-statements
        """Update the passed organization with the new info."""
        current_app.logger.debug('<update_org ')

        has_org_updates: bool = False  # update the org table if this variable is set true
        has_status_changing: bool = False

        org_model: OrgModel = self._model
        # to enforce necessary details for govm account creation
        is_govm_account = org_model.access_type == AccessType.GOVM.value
        is_govm_account_creation = \
            is_govm_account and org_model.status_code == OrgStatus.PENDING_INVITE_ACCEPT.value

        # validate if name or branch name is getting updatedtest_org.py
        branch_name = org_info.get('branchName', None)
        org_name = org_info.get('name', None)
        current_org_name = org_name or org_model.name
        name_updated = branch_name or org_name
        if name_updated:
            arg_dict = {'name': current_org_name,
                        'branch_name': branch_name,
                        'org_id': org_model.id}
            duplicate_org_name_validate(is_fatal=True, **arg_dict)

        # If the account is created using BCOL credential, verify its valid bc online account
        # If it's a valid account disable the current one and add a new one
        if bcol_credential := org_info.pop('bcOnlineCredential', None):
            bcol_response = Org.get_bcol_details(bcol_credential, self._model.id).json()
            Org._map_response_to_org(bcol_response, org_info, do_link_name=False)
            ProductService.create_subscription_from_bcol_profile(org_model.id, bcol_response.get('profileFlags'))
            has_org_updates = True

        product_subscriptions = org_info.pop('productSubscriptions', None)

        mailing_address = org_info.pop('mailingAddress', None)
        payment_info = org_info.pop('paymentInfo', {})
        Org._is_govm_missing_account_data(is_govm_account_creation, mailing_address, payment_info.get('revenueAccount'))

        if is_govm_account_creation:
            has_org_updates = True
            org_info['statusCode'] = OrgStatus.PENDING_STAFF_REVIEW.value
            has_status_changing = True
            self._create_gov_account_task(org_model)
        if product_subscriptions is not None:
            subscription_data = {'subscriptions': product_subscriptions}
            ProductService.create_product_subscription(self._model.id, subscription_data=subscription_data,
                                                       skip_auth=True)

        # Update mailing address Or create new one
        if mailing_address:
            has_org_updates = True
            contacts = self._model.contacts
            if len(contacts) > 0:
                contact = self._model.contacts[0].contact
                contact.update_from_dict(**camelback2snake(mailing_address))
                contact.save()
            else:
                Org.add_contact_to_org(mailing_address, self._model)

        # Check for other variables
        if org_info:  # Once all org info are popped and variables remains, update the org.
            has_org_updates = True

        if has_org_updates:
            excluded = ('type_code',) if has_status_changing else EXCLUDED_FIELDS
            self._model.update_org_from_dict(camelback2snake(org_info), exclude=excluded)
            if is_govm_account_creation:
                # send mail after the org is committed to DB
                Org.send_staff_review_account_reminder(relationship_id=self._model.id)

        if name_updated or payment_info:
            Org._create_payment_for_org(mailing_address, self._model, payment_info, False)
        Org._publish_activity_on_mailing_address_change(org_model.id, current_org_name, mailing_address)
        Org._publish_activity_on_name_change(org_model.id, org_name)

        ProductService.update_org_product_keycloak_groups(org_model.id)
        current_app.logger.debug('>update_org ')
        return self

    @staticmethod
    def _is_govm_missing_account_data(is_govm_account_creation, mailing_address, revenue_account):
        if is_govm_account_creation and (mailing_address is None or revenue_account is None):
            raise BusinessException(Error.GOVM_ACCOUNT_DATA_MISSING, None)

    @staticmethod
    def _publish_activity_on_mailing_address_change(org_id: int, org_name: str, mailing_address: str):
        if mailing_address:
            ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.ACCOUNT_ADDRESS_CHANGE.value,
                                                           name=org_name, value=json.dumps(mailing_address)))

    @staticmethod
    def _publish_activity_on_name_change(org_id: int, org_name: str):
        if org_name:
            ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.ACCOUNT_NAME_CHANGE.value,
                                                           name=org_name, value=org_name))

    @staticmethod
    def _create_payment_for_org(mailing_address, org, payment_info, is_new_org: bool = True) -> PaymentAccountStatus:
        """Create Or update payment info for org."""
        selected_payment_method = payment_info.get('paymentMethod', None)
        payment_method = None
        arg_dict = {'selected_payment_method': selected_payment_method,
                    'access_type': org.access_type,
                    'org_type': OrgType[org.type_code]
                    }
        if is_new_org or selected_payment_method:
            validator_obj = payment_type_validate(is_fatal=True, **arg_dict)
            payment_method = validator_obj.info.get('payment_type')
        Org._create_payment_settings(org, payment_info, payment_method, mailing_address, is_new_org)

    @staticmethod
    def _create_gov_account_task(org_model: OrgModel):
        # create a staff review task for this account
        task_type = TaskTypePrefix.GOVM_REVIEW.value
        user: UserModel = UserModel.find_by_jwt_token()
        task_info = {'name': org_model.name,
                     'relationshipId': org_model.id,
                     'relatedTo': user.id,
                     'dateSubmitted': datetime.today(),
                     'relationshipType': TaskRelationshipType.ORG.value,
                     'type': task_type,
                     'action': TaskAction.ACCOUNT_REVIEW.value,
                     'status': TaskStatus.OPEN.value,
                     'relationship_status': TaskRelationshipStatus.PENDING_STAFF_REVIEW.value
                     }
        TaskService.create_task(task_info=task_info, do_commit=False)

    @staticmethod
    def delete_org(org_id):
        """Soft-Deletes an Org.

        Only admin can perform this.
        1 - All businesses gets unaffiliated.
        2 - All team members removed.
        3 - If there is any credit on the account then cannot be deleted.

        Premium:
        1 - If there is any active PAD transactions going on, then cannot be deleted.

        """
        current_app.logger.debug(f'<Delete Org {org_id}')
        # Affiliation uses OrgService, adding as local import
        # pylint:disable=import-outside-toplevel, cyclic-import
        from auth_api.services.affiliation import Affiliation as AffiliationService

        check_auth(one_of_roles=(ADMIN, STAFF), org_id=org_id)

        org: OrgModel = OrgModel.find_by_org_id(org_id)
        if not org:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if org.status_code not in (OrgStatus.ACTIVE.value, OrgStatus.PENDING_INVITE_ACCEPT.value):
            raise BusinessException(Error.NOT_ACTIVE_ACCOUNT, None)

        # Deactivate pay account
        Org._delete_pay_account(org_id)

        # Find all active affiliations and remove them.
        entities = AffiliationService.find_affiliations_by_org_id(org_id)
        for entity in entities:
            delete_affiliation_request = DeleteAffiliationRequest(org_id=org_id,
                                                                  business_identifier=entity['business_identifier'],
                                                                  reset_passcode=True)
            AffiliationService.delete_affiliation(delete_affiliation_request)

        # Deactivate all members.
        members = MembershipModel.find_members_by_org_id(org_id)
        for member in members:
            member.status = Status.INACTIVE.value
            member.flush()

            user: UserModel = UserModel.find_by_id(member.user_id)
            # Remove user from keycloak group if they are not part of any orgs
            if len(MembershipModel.find_orgs_for_user(member.user_id)) == 0:
                KeycloakService.remove_from_account_holders_group(user.keycloak_guid)

            # If the admin is BCeID user, mark the affidavit INACTIVE.
            if user.login_source == LoginSource.BCEID.value and member.membership_type_code == ADMIN:
                affidavit: AffidavitModel = AffidavitModel.find_approved_by_user_id(user.id)
                if affidavit:
                    affidavit.status_code = AffidavitStatus.INACTIVE.value
                    affidavit.flush()

        # Set the account as INACTIVE
        org.status_code = OrgStatus.INACTIVE.value
        org.save()

        ProductService.update_org_product_keycloak_groups(org.id)

        current_app.logger.debug('org Inactivated>')

    @staticmethod
    def _delete_pay_account(org_id):
        pay_url = current_app.config.get('PAY_API_URL')
        try:
            token = RestService.get_service_account_token()
            pay_response = RestService.delete(endpoint=f'{pay_url}/accounts/{org_id}', token=token,
                                              raise_for_status=False)
            pay_response.raise_for_status()
        except HTTPError as pay_err:
            current_app.logger.info(pay_err)
            response_json = pay_response.json()
            error_type = response_json.get('type')
            error: Error = Error[error_type] if error_type in Error.__members__ else Error.PAY_ACCOUNT_DEACTIVATE_ERROR
            raise BusinessException(error, pay_err) from pay_err

    def get_payment_info(self):
        """Return the Payment Details for an org by calling Pay API."""
        pay_url = current_app.config.get('PAY_API_URL')
        # invoke pay-api
        token = RestService.get_service_account_token()
        response = RestService.get(endpoint=f'{pay_url}/accounts/{self._model.id}', token=token, retry_on_failure=True)
        return response.json()

    @staticmethod
    def find_by_org_id(org_id, allowed_roles: Tuple = None):
        """Find and return an existing organization with the provided id."""
        if org_id is None:
            return None

        org_model = OrgModel.find_by_org_id(org_id)
        if not org_model:
            return None

        # Check authorization for the user
        check_auth(one_of_roles=allowed_roles, org_id=org_id)

        return Org(org_model)

    @staticmethod
    def find_by_org_name(org_name, branch_name=None):
        """Find and return an existing organization with the provided name."""
        if org_name is None:
            return None

        org_model = OrgModel.find_similar_org_by_name(org_name, org_id=None, branch_name=branch_name)
        if not org_model:
            return None

        orgs = {'orgs': []}

        for org in org_model:
            orgs['orgs'].append(Org(org).as_dict())

        return orgs

    @staticmethod
    def get_login_options_for_org(org_id, allowed_roles: Tuple = None):
        """Get the payment settings for the given org."""
        current_app.logger.debug('get_login_options(>')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Check authorization for the user
        check_auth(one_of_roles=allowed_roles, org_id=org_id)
        return AccountLoginOptionsModel.find_active_by_org_id(org_id)

    @staticmethod
    def add_login_option(org_id, login_source):
        """Create a new contact for this org."""
        # check for existing contact (only one contact per org for now)
        current_app.logger.debug('>add_login_option')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        check_auth(one_of_roles=ADMIN, org_id=org_id)

        login_option = AccountLoginOptionsModel(login_source=login_source, org_id=org_id)
        login_option.save()
        return login_option

    @staticmethod
    def update_login_option(org_id, login_source):
        """Create a new contact for this org."""
        # check for existing contact (only one contact per org for now)
        current_app.logger.debug('>update_login_option')
        org = OrgModel.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        check_auth(one_of_roles=ADMIN, org_id=org_id)

        existing_login_option = AccountLoginOptionsModel.find_active_by_org_id(org_id)
        if existing_login_option is not None:
            existing_login_option.is_active = False
            existing_login_option.add_to_session()

        login_option = AccountLoginOptionsModel(login_source=login_source, org_id=org_id)
        login_option.save()
        ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.AUTHENTICATION_METHOD_CHANGE.value,
                                                       name=org.name, value=login_source,
                                                       id=login_option.id))
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

    @staticmethod
    def get_orgs(user_id, valid_statuses=VALID_STATUSES):
        """Return the orgs associated with this user."""
        return MembershipModel.find_orgs_for_user(user_id, valid_statuses)

    @staticmethod
    def search_orgs(search: OrgSearch, environment):  # pylint: disable=too-many-locals
        """Search for orgs based on input parameters."""
        orgs_result = {
            'orgs': [],
            'page': search.page,
            'limit': search.limit,
            'total': 0
        }
        include_invitations: bool = False
        search.access_type, is_staff_admin = Org.refine_access_type(search.access_type)
        if search.statuses and OrgStatus.PENDING_ACTIVATION.value in search.statuses:
            # only staff admin can see director search accounts
            if not is_staff_admin:
                raise BusinessException(Error.INVALID_USER_CREDENTIALS, None)
            org_models, orgs_result['total'] = OrgModel.search_pending_activation_orgs(name=search.name)
            include_invitations = True
        else:
            org_models, orgs_result['total'] = OrgModel.search_org(search, environment)

        for org in org_models:
            orgs_result['orgs'].append({
                **Org(org).as_dict(),
                'contacts': [ContactSchema(exclude=('links',)).dump(org.contacts[0].contact, many=False)]
                if org.contacts else [],
                'invitations': [
                    InvitationSchema(exclude=('membership',)).dump(org.invitations[0].invitation, many=False)
                ]
                if include_invitations and org.invitations else [],
            })
        return orgs_result

    @staticmethod
    def search_orgs_by_affiliation(business_identifier,
                                   pagination_info: PaginationInfo, environment):
        """Search for orgs based on input parameters."""
        orgs, total = OrgModel.search_orgs_by_business_identifier(business_identifier, pagination_info, environment)

        return {
            'orgs': orgs,
            'page': pagination_info.page,
            'limit': pagination_info.limit,
            'total': total
        }

    @staticmethod
    @user_context
    def refine_access_type(access_types, **kwargs):
        """Find Access Type."""
        user_from_context: UserContext = kwargs['user_context']
        roles = user_from_context.roles

        is_staff_admin = Role.STAFF_CREATE_ACCOUNTS.value in roles or Role.STAFF_MANAGE_ACCOUNTS.value in roles
        if not is_staff_admin:
            if len(access_types) < 1:
                # pass everything except DIRECTOR SEARCH
                access_types = [item.value for item in AccessType if item != AccessType.ANONYMOUS]
            else:
                access_types.remove(AccessType.ANONYMOUS.value)
        return access_types, is_staff_admin

    @staticmethod
    def bcol_account_link_check(bcol_account_id, org_id=None):
        """Validate the BCOL id is linked or not. If already linked, return True."""
        if current_app.config.get('BCOL_ACCOUNT_LINK_CHECK'):
            org = OrgModel.find_by_bcol_id(bcol_account_id)
            if org and org.id != org_id:  # check if already taken up by different org
                return True

        return False

    def change_org_status(self, status_code, suspension_reason_code):
        """Update the status of the org.

        Used now for suspending/activate account.

            1) check access .only staff can do it now
            2) check org status/eligiblity
            3) suspend it

        """
        current_app.logger.debug('<change_org_status ')

        user: UserModel = UserModel.find_by_jwt_token()
        org_model = self._model
        org_model.status_code = status_code
        org_model.decision_made_by = user.username  # not sure if a new field is needed for this.
        if status_code == OrgStatus.SUSPENDED.value:
            org_model.suspended_on = datetime.today()
            org_model.suspension_reason_code = suspension_reason_code
        org_model.save()
        if status_code == OrgStatus.SUSPENDED.value:
            suspension_reason_description = SuspensionReasonCode[suspension_reason_code].value \
                if suspension_reason_code in [
                item.name for item in SuspensionReasonCode] else ''
            ActivityLogPublisher.publish_activity(Activity(org_model.id, ActivityAction.ACCOUNT_SUSPENSION.value,
                                                           name=org_model.name,
                                                           value=suspension_reason_description))
        current_app.logger.debug('change_org_status>')
        return Org(org_model)

    @staticmethod
    def approve_or_reject(org_id: int, is_approved: bool, origin_url: str = None,
                          task_action: str = None):
        """Mark the affidavit as approved or rejected."""
        current_app.logger.debug('<find_affidavit_by_org_id ')
        # Get the org and check what's the current status
        org: OrgModel = OrgModel.find_by_org_id(org_id)

        # Current User
        user: UserModel = UserModel.find_by_jwt_token()

        if task_action == TaskAction.AFFIDAVIT_REVIEW.value:
            AffidavitService.approve_or_reject(org_id, is_approved, user)

        if is_approved:
            org.status_code = OrgStatus.ACTIVE.value
        else:
            org.status_code = OrgStatus.REJECTED.value

        org.decision_made_by = user.username
        org.decision_made_on = datetime.now()

        # TODO Publish to activity stream

        org.save()
        # Find admin email addresses
        admin_emails = UserService.get_admin_emails_for_org(org_id)
        if admin_emails != '':
            if org.access_type in (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value):
                Org.send_approved_rejected_notification(admin_emails, org.name, org.id, org.status_code, origin_url)
            elif org.access_type in (AccessType.GOVM.value, AccessType.GOVN.value):
                Org.send_approved_rejected_govm_govn_notification(admin_emails, org.name, org.id, org.status_code,
                                                                  origin_url)
        else:
            # continue but log error
            current_app.logger.error('No admin email record for org id %s', org_id)

        current_app.logger.debug('>find_affidavit_by_org_id ')
        return Org(org)

    @staticmethod
    def send_staff_review_account_reminder(relationship_id,
                                           task_relationship_type=TaskRelationshipType.ORG.value):
        """Send staff review account reminder notification."""
        current_app.logger.debug('<send_staff_review_account_reminder')
        user: UserModel = UserModel.find_by_jwt_token()
        recipient = current_app.config.get('STAFF_ADMIN_EMAIL')
        # Get task id that is related with the task. Task Relationship Type can be ORG, PRODUCT etc.
        task = TaskModel.find_by_task_relationship_id(task_relationship_type=task_relationship_type,
                                                      relationship_id=relationship_id)
        context_path = f'review-account/{task.id}'
        app_url = f"{g.get('origin_url', '')}/{current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH')}"
        review_url = f'{app_url}/{context_path}'
        first_name = user.firstname
        last_name = user.lastname

        data = {
            'emailAddresses': recipient,
            'contextUrl': review_url,
            'userFirstName': first_name,
            'userLastName': last_name
        }
        try:
            publish_to_mailer('staffReviewAccount', org_id=relationship_id, data=data)
            current_app.logger.debug('<send_staff_review_account_reminder')
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_staff_review_account_reminder failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e

    @staticmethod
    def send_approved_rejected_notification(receipt_admin_emails, org_name, org_id, org_status: OrgStatus, origin_url):
        """Send Approved/Rejected notification to the user."""
        current_app.logger.debug('<send_approved_rejected_notification')

        if org_status == OrgStatus.ACTIVE.value:
            notification_type = 'nonbcscOrgApprovedNotification'
        elif org_status == OrgStatus.REJECTED.value:
            notification_type = 'nonbcscOrgRejectedNotification'
        else:
            return  # Don't send mail for any other status change
        app_url = f"{origin_url}/{current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH')}"
        data = {
            'accountId': org_id,
            'emailAddresses': receipt_admin_emails,
            'contextUrl': app_url,
            'orgName': org_name
        }
        try:
            publish_to_mailer(notification_type, org_id=org_id, data=data)
            current_app.logger.debug('<send_approved_rejected_notification')
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_approved_rejected_notification failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e

    @staticmethod
    def send_approved_rejected_govm_govn_notification(receipt_admin_email, org_name, org_id, org_status: OrgStatus,
                                                      origin_url):
        """Send Approved govm notification to the user."""
        current_app.logger.debug('<send_approved_rejected_govm_govn_notification')

        if org_status == OrgStatus.ACTIVE.value:
            notification_type = 'govmApprovedNotification'
        elif org_status == OrgStatus.REJECTED.value:
            notification_type = 'govmRejectedNotification'
        else:
            return  # Don't send mail for any other status change
        app_url = f"{origin_url}/{current_app.config.get('AUTH_WEB_TOKEN_CONFIRM_PATH')}"
        data = {
            'accountId': org_id,
            'emailAddresses': receipt_admin_email,
            'contextUrl': app_url,
            'orgName': org_name
        }
        try:
            publish_to_mailer(notification_type, org_id=org_id, data=data)
            current_app.logger.debug('send_approved_rejected_govm_govn_notification>')
        except Exception as e:  # noqa=B901
            current_app.logger.error('<send_approved_rejected_govm_govn_notification failed')
            raise BusinessException(Error.FAILED_NOTIFICATION, None) from e

    def change_org_access_type(self, access_type):
        """Update the access type of the org."""
        current_app.logger.debug('<change_org_access_type ')
        org_model = self._model
        org_model.access_type = access_type
        org_model.save()
        current_app.logger.debug('change_org_access_type>')
        return Org(org_model)

    def patch_org(self, action: str = None, request_json: Dict[str, any] = None):
        """Update Org."""
        if (patch_action := PatchActions.from_value(action)) is None:
            raise BusinessException(Error.PATCH_INVALID_ACTION, None)

        if patch_action == PatchActions.UPDATE_STATUS:
            status_code = request_json.get('statusCode', None)
            suspension_reason_code = request_json.get('suspensionReasonCode', None)
            if status_code is None:
                raise BusinessException(Error.INVALID_INPUT, None)
            if status_code == OrgStatus.SUSPENDED.value and suspension_reason_code is None:
                raise BusinessException(Error.INVALID_INPUT, None)
            return self.change_org_status(status_code, suspension_reason_code).as_dict()
        if patch_action == PatchActions.UPDATE_ACCESS_TYPE:
            access_type = request_json.get('accessType', None)
            # Currently, only accounts with the following access types can be updated
            if access_type is None or access_type not in [AccessType.REGULAR.value, AccessType.REGULAR_BCEID.value,
                                                          AccessType.EXTRA_PROVINCIAL.value, AccessType.GOVN.value]:
                raise BusinessException(Error.INVALID_INPUT, None)
            return self.change_org_access_type(access_type).as_dict()
        return None
