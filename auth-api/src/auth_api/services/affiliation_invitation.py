# Copyright © 2023 Province of British Columbia
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
"""Service for managing Affiliation Invitation data."""
from datetime import datetime
from typing import Dict
from urllib.parse import urlencode

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from jinja2 import Environment, FileSystemLoader
from requests.exceptions import HTTPError
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.config import get_named_config
from auth_api.exceptions import BusinessException, ServiceUnavailableException
from auth_api.exceptions.errors import Error
from auth_api.models import AccountLoginOptions as AccountLoginOptionsModel
from auth_api.models import AffiliationInvitation as AffiliationInvitationModel
from auth_api.models import InvitationStatus as InvitationStatusModel
from auth_api.models import Membership as MembershipModel
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.entity import Entity as EntityModel
from auth_api.models.org import Org as OrgModel
from auth_api.schemas import AffiliationInvitationSchema
from auth_api.services.entity import Entity as EntityService
from auth_api.services.user import User as UserService
from auth_api.utils.enums import AccessType, AffiliationInvitationType, InvitationStatus, LoginSource, Status
from auth_api.utils.roles import ADMIN, COORDINATOR, STAFF
from auth_api.utils.user_context import UserContext, user_context

from ..utils.account_mailer import publish_to_mailer
from ..utils.passcode import validate_passcode
from ..utils.util import escape_wam_friendly_url
from .authorization import check_auth
from .rest_service import RestService


ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)
CONFIG = get_named_config()


class AffiliationInvitation:
    """Manages Affiliation Invitation data.

    This service manages creating, updating, and retrieving Affiliation Invitation data via
    the Affiliation Invitation model.
    """

    def __init__(self, model):
        """Return an affiliation invitation service instance."""
        self._model = model

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the Affiliation Invitation model as a dictionary."""
        affiliation_invitation_schema = AffiliationInvitationSchema()
        obj = affiliation_invitation_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    @user_context
    def create_affiliation_invitation(affiliation_invitation_info: Dict,
                                      # pylint:disable=unused-argument,too-many-locals
                                      user, invitation_origin, **kwargs):
        """Create a new affiliation invitation."""
        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        from_org_id = affiliation_invitation_info['fromOrgId']
        to_org_id = affiliation_invitation_info['toOrgId']
        business_identifier = affiliation_invitation_info['businessIdentifier']

        check_auth(org_id=from_org_id,
                   business_identifier=business_identifier,
                   one_of_roles=(ADMIN, COORDINATOR, STAFF))

        # Validate from/to organizations exists
        if not (from_org := OrgModel.find_by_org_id(from_org_id)):
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        if not OrgModel.find_by_org_id(to_org_id):
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Validate that entity exists
        if not (entity := EntityService.find_by_business_identifier(business_identifier, skip_auth=True)):
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Check if affiliation already exists
        if AffiliationModel.find_affiliation_by_org_and_entity_ids(to_org_id, entity.identifier):
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        # Check if an affiliation invitation already exists
        if AffiliationInvitationModel.find_invitations_by_org_entity_ids(from_org_id=from_org_id,
                                                                         to_org_id=to_org_id,
                                                                         entity_id=entity.identifier):
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        affiliation_invitation_info['entityId'] = entity.identifier

        if from_org.access_type == AccessType.ANONYMOUS.value:  # anonymous account never get bceid or bcsc choices
            mandatory_login_source = LoginSource.BCROS.value
        elif from_org.access_type == AccessType.GOVM.value:
            mandatory_login_source = LoginSource.STAFF.value
        else:
            default_login_option_based_on_accesstype = LoginSource.BCSC.value if \
                from_org.access_type == AccessType.REGULAR.value else LoginSource.BCEID.value
            account_login_options = AccountLoginOptionsModel.find_active_by_org_id(from_org.id)
            mandatory_login_source = getattr(account_login_options, 'login_source',
                                             default_login_option_based_on_accesstype)

        # If a pass code is provided check if it is correct
        if pass_code := affiliation_invitation_info.get('passCode'):
            if not validate_passcode(pass_code, entity.pass_code):
                raise BusinessException(Error.INVALID_USER_CREDENTIALS, None)

            affiliation_invitation_info['type'] = AffiliationInvitationType.PASSCODE.value

        affiliation_invitation = AffiliationInvitationModel.create_from_dict(affiliation_invitation_info,
                                                                             user.identifier)
        confirmation_token = AffiliationInvitation.generate_confirmation_token(affiliation_invitation.id,
                                                                               from_org_id, to_org_id,
                                                                               business_identifier)
        affiliation_invitation.token = confirmation_token
        affiliation_invitation.login_source = mandatory_login_source
        affiliation_invitation.save()

        if affiliation_invitation.type != AffiliationInvitationType.PASSCODE.value:
            # Fetch the up-to-date business details from legal API
            token = RestService.get_service_account_token(config_id='ENTITY_SVC_CLIENT_ID',
                                                          config_secret='ENTITY_SVC_CLIENT_SECRET')
            business = AffiliationInvitation._get_business_details(business_identifier, token)
            AffiliationInvitation.send_affiliation_invitation(affiliation_invitation,
                                                              business['business']['legalName'],
                                                              f'{invitation_origin}/{context_path}')
        else:
            return AffiliationInvitation.accept_affiliation_invitation(affiliation_invitation.id,
                                                                       user, invitation_origin,
                                                                       **kwargs)
        return AffiliationInvitation(affiliation_invitation)

    @staticmethod
    def _get_business_details(business_identifier: str, token: str):
        """Return business details by calling legal-api."""
        legal_api_url = current_app.config.get('LEGAL_API_URL') + current_app.config.get('LEGAL_API_VERSION_2')
        get_businesses_url = f'{ legal_api_url }/businesses/{business_identifier}'
        try:
            get_business_response = RestService.get(get_businesses_url, token=token, skip_404_logging=True)
        except (HTTPError, ServiceUnavailableException) as e:
            current_app.logger.info(e)
            raise BusinessException(Error.DATA_NOT_FOUND, None) from e

        return get_business_response.json()

    def update_affiliation_invitation(self, user, invitation_origin, affiliation_invitation_info: Dict):
        """Update the specified affiliation invitation with new data."""
        check_auth(org_id=self._model.from_org_id,
                   business_identifier=self._model.entity.business_identifier,
                   one_of_roles=(ADMIN, COORDINATOR, STAFF))

        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        invitation: AffiliationInvitationModel = self._model

        # Don't do any updates if the invitation is not in PENDING state
        if invitation.invitation_status_code != InvitationStatus.PENDING.value:
            return AffiliationInvitation(invitation)

        # Check for status to patch
        new_status = affiliation_invitation_info.get('status')
        if not new_status or new_status == InvitationStatus.PENDING.value:
            # Resend invitation
            confirmation_token = AffiliationInvitation\
                .generate_confirmation_token(self._model.id,
                                             self._model.from_org_id,
                                             self._model.to_org_id,
                                             self._model.entity.business_identifier)
            self._model.token = confirmation_token
            invitation = self._model.update_invitation_as_retried(user.identifier)
            entity: EntityModel = invitation.entity

            business = AffiliationInvitation._get_business_details(entity.business_identifier,
                                                                   RestService.get_service_account_token())

            AffiliationInvitation.send_affiliation_invitation(invitation,
                                                              business['business']['legalName'],
                                                              f'{invitation_origin}/{context_path}')
        # Expire invitation
        elif new_status == InvitationStatus.EXPIRED.value:
            invitation = self._model.expire_invitation()

        return AffiliationInvitation(invitation)

    @staticmethod
    def delete_affiliation_invitation(invitation_id):
        """Delete the specified affiliation invitation."""
        if not (invitation := AffiliationInvitationModel.find_invitation_by_id(invitation_id)):
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        if invitation.status == InvitationStatus.ACCEPTED.value:
            raise BusinessException(Error.ACTIONED_AFFILIATION_INVITATION, None)

        check_auth(org_id=invitation.from_org_id, one_of_roles=(ADMIN, COORDINATOR, STAFF))

        invitation.delete()

    @staticmethod
    @user_context
    def get_invitations_for_from_org(org_id, status=None, **kwargs):
        """Get affiliation invitations for from org."""
        user_from_context: UserContext = kwargs['user_context']

        if not OrgModel.find_by_org_id(org_id):
            return None

        if status:
            status = InvitationStatus[status]

        # If staff return full list
        if user_from_context.is_staff():
            return AffiliationInvitationModel.find_pending_invitations_by_from_org(org_id)

        current_user: UserService = UserService.find_by_jwt_token()
        current_user_membership: MembershipModel = \
            MembershipModel.find_membership_by_user_and_org(user_id=current_user.identifier, org_id=org_id)

        # If no active membership return empty array
        if current_user_membership is None or \
                current_user_membership.status != Status.ACTIVE.value:
            return []

        return AffiliationInvitationModel.find_invitations_from_org(org_id=org_id, status=status)

    @staticmethod
    @user_context
    def search_invitations_for_from_org(org_id, status=None, **kwargs):
        """Search affiliation invitations for from org."""
        invitation_models = AffiliationInvitation.get_invitations_for_from_org(org_id, status, **kwargs) or []
        invitations_result = {
            'affiliationInvitations': [AffiliationInvitation(invitation).as_dict()
                                       for invitation in invitation_models]
        }

        return invitations_result

    @staticmethod
    @user_context
    def get_invitations_for_to_org(org_id, status=None, **kwargs):
        """Get affiliation invitations for to org."""
        user_from_context: UserContext = kwargs['user_context']

        if not OrgModel.find_by_org_id(org_id):
            return None

        if status:
            status = InvitationStatus[status]

        # If staff return full list
        if user_from_context.is_staff():
            return AffiliationInvitationModel.find_pending_invitations_by_to_org(org_id)

        current_user: UserService = UserService.find_by_jwt_token()
        current_user_membership: MembershipModel = \
            MembershipModel.find_membership_by_user_and_org(user_id=current_user.identifier, org_id=org_id)

        # If no active membership return empty array
        if current_user_membership is None or \
                current_user_membership.status != Status.ACTIVE.value:
            return []

        return AffiliationInvitationModel.find_invitations_to_org(org_id=org_id, status=status)

    @staticmethod
    def find_affiliation_invitation_by_id(invitation_id):
        """Find an existing affiliation invitation with the provided id."""
        if invitation_id is None:
            return None

        if not (invitation := AffiliationInvitationModel.find_invitation_by_id(invitation_id)):
            return None

        return AffiliationInvitation(invitation)

    @staticmethod
    def send_affiliation_invitation(affiliation_invitation: AffiliationInvitationModel, business_name, app_url,
                                    query_params: Dict[str, any] = None):
        """Send the email notification."""
        current_app.logger.debug('<send_affiliation_invitation')
        org_name = affiliation_invitation.to_org.name
        org_id = affiliation_invitation.to_org_id
        mail_configs = AffiliationInvitation._get_affiliation_invitation_configs(org_name)
        recipient = affiliation_invitation.recipient_email
        token_confirm_url = f"{app_url}/{mail_configs.get('token_confirm_path')}/{affiliation_invitation.token}"
        if query_params:
            token_confirm_url += f'?{urlencode(query_params)}'

        data = {
            'accountId': org_id,
            'businessName': business_name,
            'emailAddresses': recipient,
            'contextUrl': token_confirm_url,
            'orgName': org_name
        }

        try:
            publish_to_mailer(notification_type=mail_configs.get('notification_type'), org_id=org_id, data=data)
        except BusinessException as exception:
            affiliation_invitation.invitation_status_code = InvitationStatus.FAILED.value
            affiliation_invitation.save()
            current_app.logger.debug('>send_affiliation_invitation failed')
            current_app.logger.debug(exception)
            raise BusinessException(Error.FAILED_AFFILIATION_INVITATION, None) from exception

        current_app.logger.debug('>send_affiliation_invitation')

    @staticmethod
    def _get_affiliation_invitation_configs(org_name):
        """Get the config for different email types."""
        escape_url = escape_wam_friendly_url(org_name)
        token_confirm_path = f'{escape_url}/affiliationInvitation/acceptToken/'

        default_configs = {
            'token_confirm_path': token_confirm_path,
            'notification_type': 'affiliationInvitation',
        }

        return default_configs

    @staticmethod
    def generate_confirmation_token(affiliation_invitation_id, from_org_id, to_org_id, business_identifier):
        """Generate the token to be sent in the email."""
        serializer = URLSafeTimedSerializer(CONFIG.EMAIL_TOKEN_SECRET_KEY)
        token = {'id': affiliation_invitation_id,
                 'fromOrgId': from_org_id,
                 'toOrgId': to_org_id,
                 'businessIdentifier': business_identifier}
        return serializer.dumps(token, salt=CONFIG.EMAIL_SECURITY_PASSWORD_SALT)

    @staticmethod
    def validate_token(token, affiliation_invitation_id: int):
        """Check whether the passed token is valid."""
        serializer = URLSafeTimedSerializer(CONFIG.EMAIL_TOKEN_SECRET_KEY)
        token_valid_for = int(CONFIG.AFFILIATION_TOKEN_EXPIRY_PERIOD_MINS) \
            * 60 if CONFIG.AFFILIATION_TOKEN_EXPIRY_PERIOD_MINS else 60 * 15
        try:
            token_payload = serializer.loads(token, salt=CONFIG.EMAIL_SECURITY_PASSWORD_SALT,
                                             max_age=token_valid_for)
            token_invitation_id = token_payload.get('id')

            # The specified affiliation_invitation_id does not match the token
            if affiliation_invitation_id != token_invitation_id:
                raise BusinessException(Error.INVALID_AFFILATION_INVITATION_TOKEN, None)

        except Exception as e:  # noqa: E722
            raise BusinessException(Error.EXPIRED_AFFILIATION_INVITATION, None) from e

        affiliation_invitation: AffiliationInvitationModel = AffiliationInvitationModel.\
            find_invitation_by_id(affiliation_invitation_id)

        if affiliation_invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if affiliation_invitation.invitation_status_code == InvitationStatus.ACCEPTED.value:
            raise BusinessException(Error.ACTIONED_AFFILIATION_INVITATION, None)
        if affiliation_invitation.invitation_status_code == InvitationStatus.EXPIRED.value:
            raise BusinessException(Error.EXPIRED_AFFILIATION_INVITATION, None)

        return AffiliationInvitation(affiliation_invitation)

    @staticmethod
    @user_context
    def accept_affiliation_invitation(affiliation_invitation_id,
                                      # pylint:disable=unused-argument
                                      user: UserService, origin, **kwargs):
        """Add an affiliation from the affilation invitation."""
        current_app.logger.debug('>accept_affiliation_invitation')
        affiliation_invitation: AffiliationInvitationModel = AffiliationInvitationModel.\
            find_invitation_by_id(affiliation_invitation_id)

        if affiliation_invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if affiliation_invitation.invitation_status_code == InvitationStatus.ACCEPTED.value:
            raise BusinessException(Error.ACTIONED_AFFILIATION_INVITATION, None)
        if affiliation_invitation.invitation_status_code == InvitationStatus.EXPIRED.value:
            raise BusinessException(Error.EXPIRED_AFFILIATION_INVITATION, None)

        org_id = affiliation_invitation.to_org_id
        entity_id = affiliation_invitation.entity_id

        if not (affiliation_model := AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id, entity_id)):
            # Create an affiliation with to_org_id
            affiliation_model = AffiliationModel(org_id=org_id, entity_id=entity_id, certified_by_name=None)
            affiliation_model.save()

        affiliation_invitation.affiliation_id = affiliation_model.id
        affiliation_invitation.approver_id = user.identifier
        affiliation_invitation.accepted_date = datetime.now()
        affiliation_invitation.invitation_status = InvitationStatusModel\
            .get_status_by_code(InvitationStatus.ACCEPTED.value)
        affiliation_invitation.save()

        current_app.logger.debug('<accept_affiliation_invitation')
        return AffiliationInvitation(affiliation_invitation)
