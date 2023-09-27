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
from dataclasses import fields
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlencode

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from jinja2 import Environment, FileSystemLoader
from requests.exceptions import HTTPError
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001
from sqlalchemy.exc import DataError

from auth_api.config import get_named_config
from auth_api.exceptions import BusinessException, ServiceUnavailableException
from auth_api.exceptions.errors import Error
from auth_api.models import AccountLoginOptions as AccountLoginOptionsModel
from auth_api.models import AffiliationInvitation as AffiliationInvitationModel
from auth_api.models import InvitationStatus as InvitationStatusModel
from auth_api.models import Membership as MembershipModel
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.dataclass import AffiliationInvitationSearch, AffiliationInvitationData
from auth_api.models.entity import Entity as EntityModel  # noqa: I005
from auth_api.models.org import Org as OrgModel
from auth_api.schemas import AffiliationInvitationSchema
from auth_api.services.entity import Entity as EntityService
from auth_api.services.org import Org as OrgService
from auth_api.services.user import User as UserService
from auth_api.utils.enums import AccessType, AffiliationInvitationType, InvitationStatus, LoginSource, Status
from auth_api.utils.roles import ADMIN, COORDINATOR, STAFF
from auth_api.utils.user_context import UserContext, user_context
from ..schemas.affiliation_invitation import AffiliationInvitationSchemaPublic

from ..utils.account_mailer import publish_to_mailer
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
    def as_dict(self, mask_email=False):
        """Return the Affiliation Invitation model as a dictionary."""
        affiliation_invitation_schema = self.get_affiliation_invitation_schema(mask_email)
        obj = affiliation_invitation_schema.dump(self._model, many=False)
        return obj

    @classmethod
    def get_affiliation_invitation_schema(cls, mask_email: bool):
        """Return the appropriate affiliation invitation schema."""
        return AffiliationInvitationSchemaPublic() if mask_email else AffiliationInvitationSchema()

    @classmethod
    def affiliation_invitations_to_dict_list(cls, models: List[AffiliationInvitationModel], mask_email=True) \
            -> List[Dict]:
        """Return list of AffiliationInvitationModels converted to list dicts."""
        schema = cls.get_affiliation_invitation_schema(mask_email)
        return [schema.dump(model) for model in models]

    @classmethod
    def enrich_affiliation_invitations_dict_list_with_business_data(cls, affiliation_invitation_dicts: List[Dict]) -> \
            List[AffiliationInvitationData]:
        """Enrich affiliation invitation model data with business details."""
        if not affiliation_invitation_dicts:
            return []

        token = RestService.get_service_account_token(
            config_id='ENTITY_SVC_CLIENT_ID',
            config_secret='ENTITY_SVC_CLIENT_SECRET')

        business_identifiers = [afi['business_identifier'] for afi in affiliation_invitation_dicts]

        business_entities = AffiliationInvitation. \
            _get_multiple_business_details(business_identifiers=business_identifiers, token=token)
        result = []

        def _init_dict_for_dataclass_from_dict(dataclass, initial_dict: Dict):
            return {field.name: initial_dict.get(field.name) for field in fields(dataclass)}

        for affiliation_invitation_dict in affiliation_invitation_dicts:
            from_org = AffiliationInvitationData.OrgDetails(
                **_init_dict_for_dataclass_from_dict(AffiliationInvitationData.OrgDetails,
                                                     affiliation_invitation_dict['from_org']))
            if to_org := affiliation_invitation_dict.get('to_org'):
                to_org = AffiliationInvitationData.OrgDetails(
                    **_init_dict_for_dataclass_from_dict(AffiliationInvitationData.OrgDetails,
                                                         affiliation_invitation_dict['to_org']))

            business_entity = next(
                (business_entity for business_entity in business_entities if
                 affiliation_invitation_dict['business_identifier'] == business_entity['identifier']),
                None)

            entity = AffiliationInvitationData.EntityDetails(business_identifier=business_entity['identifier'],
                                                             name=business_entity['legalName'],
                                                             state=business_entity['state'],
                                                             corp_type=business_entity['legalType'],
                                                             corp_sub_type=business_entity.get('legalSubType', None)
                                                             ) if business_entity else None

            aid = AffiliationInvitationData(
                **{
                    **_init_dict_for_dataclass_from_dict(AffiliationInvitationData, affiliation_invitation_dict),
                    'from_org': from_org,
                    'to_org': to_org,
                    'entity': entity
                }
            )
            result.append(aid)

        return result

    @staticmethod
    def _validate_prerequisites(business_identifier, from_org_id, to_org_id,
                                affiliation_invitation_type=AffiliationInvitationType.EMAIL):
        # Validate from organizations exists
        if not (from_org := OrgModel.find_by_org_id(from_org_id)):
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Validate to organization exists if it is provided
        if to_org_id and not OrgModel.find_by_org_id(to_org_id):
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Validate business exists in LEAR
        # Fetch the up-to-date business details from legal API - Business exception raised if failure
        token = RestService.get_service_account_token(config_id='ENTITY_SVC_CLIENT_ID',
                                                      config_secret='ENTITY_SVC_CLIENT_SECRET')
        business = AffiliationInvitation._get_business_details(business_identifier, token)

        # Validate that entity exists
        if not (entity := EntityService.find_by_business_identifier(business_identifier, skip_auth=True)):
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Validate that entity contact exists
        if not (contact := entity.get_contact()) and \
                affiliation_invitation_type != AffiliationInvitationType.REQUEST:
            raise BusinessException(Error.INVALID_BUSINESS_EMAIL, None)

        # Validate that entity contact email exists
        if contact and not contact.email:
            raise BusinessException(Error.INVALID_BUSINESS_EMAIL, None)

        # Check if affiliation already exists
        if AffiliationModel.find_affiliation_by_org_and_entity_ids(from_org_id, entity.identifier):
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        # Check if an affiliation invitation already exists
        if AffiliationInvitationModel.find_invitations_by_org_entity_ids(from_org_id=from_org_id,
                                                                         entity_id=entity.identifier):
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)
        return entity, from_org, business

    @staticmethod
    def get_invitation_email(affiliation_invitation_type: AffiliationInvitationType,
                             entity: Optional[EntityService] = None,
                             org_id: Optional[int] = None) -> Optional[str]:
        """Get affiliation invitation email based on provided params."""
        if affiliation_invitation_type == AffiliationInvitationType.REQUEST:
            admin_emails = UserService.get_admin_emails_for_org(org_id)
            if admin_emails != '':
                current_app.logger.debug(f'Sending emails to: ${admin_emails}')
                return admin_emails

            # continue but log error
            current_app.logger.error('No admin email record for org id %s', org_id)
            return None

        if affiliation_invitation_type == AffiliationInvitationType.EMAIL:
            return entity.get_contact().email

        return None

    @staticmethod
    def _get_invitation_email(affiliation_invitation_info: Dict,
                              entity: OrgService = None, org_id: Optional[int] = None) -> Optional[str]:
        if invitation_type := AffiliationInvitationType.\
                from_value(affiliation_invitation_info.get('type', AffiliationInvitationType.EMAIL.value)):
            return AffiliationInvitation.get_invitation_email(affiliation_invitation_type=invitation_type,
                                                              entity=entity, org_id=org_id)

        return affiliation_invitation_info.get('recipientEmail', None)

    @staticmethod
    def _get_org_id_from_org_uuid(to_org_uuid):
        try:
            to_org: OrgModel = OrgModel.find_by_org_uuid(to_org_uuid)

            if not to_org:
                raise BusinessException(Error.DATA_NOT_FOUND, None)

            return to_org.id

        except DataError as err:
            raise BusinessException(Error.INVALID_INPUT, err) from err

    @staticmethod
    @user_context
    def create_affiliation_invitation(affiliation_invitation_info: Dict,
                                      # pylint:disable=unused-argument,too-many-locals
                                      user, invitation_origin, **kwargs):
        """Create a new affiliation invitation."""
        context_path = CONFIG.AUTH_WEB_TOKEN_CONFIRM_PATH
        from_org_id = affiliation_invitation_info['fromOrgId']
        if to_org_uuid := affiliation_invitation_info.get('toOrgUuid'):
            affiliation_invitation_info['toOrgId'] = AffiliationInvitation._get_org_id_from_org_uuid(to_org_uuid)
        to_org_id = affiliation_invitation_info.get('toOrgId')

        business_identifier = affiliation_invitation_info['businessIdentifier']
        affiliation_invitation_type = AffiliationInvitationType.from_value(affiliation_invitation_info.get('type'))

        if from_org_id == to_org_id:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        check_auth(org_id=from_org_id,
                   one_of_roles=(ADMIN, COORDINATOR, STAFF))

        entity, from_org, business = AffiliationInvitation. \
            _validate_prerequisites(business_identifier=business_identifier, from_org_id=from_org_id,
                                    to_org_id=to_org_id, affiliation_invitation_type=affiliation_invitation_type)

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

        affiliation_invitation_info['recipientEmail'] = \
            AffiliationInvitation._get_invitation_email(affiliation_invitation_info=affiliation_invitation_info,
                                                        entity=entity,
                                                        org_id=to_org_id)

        affiliation_invitation = AffiliationInvitationModel.create_from_dict(affiliation_invitation_info,
                                                                             user.identifier)
        confirmation_token = AffiliationInvitation.generate_confirmation_token(affiliation_invitation.id,
                                                                               from_org_id, to_org_id,
                                                                               business_identifier)
        affiliation_invitation.token = confirmation_token
        affiliation_invitation.login_source = mandatory_login_source
        affiliation_invitation.save()

        AffiliationInvitation\
            .send_affiliation_invitation(affiliation_invitation=affiliation_invitation,
                                         business_name=business['business']['legalName'],
                                         app_url=AffiliationInvitation._get_app_url(invitation_origin,
                                                                                    context_path),
                                         email_addresses=affiliation_invitation.recipient_email)
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
            raise BusinessException(Error.AFFILIATION_INVITATION_BUSINESS_NOT_FOUND, None) from e

        return get_business_response.json()

    @staticmethod
    def _get_multiple_business_details(business_identifiers: List[str], token: str) -> List:
        """Return json of multiple business details by calling legal-api."""
        legal_api_url = current_app.config.get('LEGAL_API_URL') + current_app.config.get('LEGAL_API_VERSION_2')
        get_businesses_url = f'{legal_api_url}/businesses/search'

        data = {'identifiers': business_identifiers}
        try:
            get_business_response = RestService.post(get_businesses_url, token=token, data=data)
        except (HTTPError, ServiceUnavailableException) as e:
            current_app.logger.info(e)
            raise BusinessException(Error.AFFILIATION_INVITATION_BUSINESS_NOT_FOUND, None) from e

        return get_business_response.json()['businessEntities']

    def update_affiliation_invitation(self, user, invitation_origin, affiliation_invitation_info: Dict):
        """Update the specified affiliation invitation with new data."""
        check_auth(org_id=self._model.from_org_id,
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

            token = RestService.get_service_account_token(config_id='ENTITY_SVC_CLIENT_ID',
                                                          config_secret='ENTITY_SVC_CLIENT_SECRET')
            business = AffiliationInvitation._get_business_details(entity.business_identifier, token)

            AffiliationInvitation\
                .send_affiliation_invitation(affiliation_invitation=invitation,
                                             business_name=business['business']['legalName'],
                                             app_url=AffiliationInvitation._get_app_url(invitation_origin,
                                                                                        context_path),
                                             email_addresses=invitation.recipient_email)
        # Expire invitation
        elif new_status == InvitationStatus.EXPIRED.value:
            invitation = self._model.set_status(InvitationStatus.EXPIRED.value)

        return AffiliationInvitation(invitation)

    @staticmethod
    def delete_affiliation_invitation(invitation_id):
        """Delete the specified affiliation invitation."""
        if not (invitation := AffiliationInvitationModel.find_invitation_by_id(invitation_id)):
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        check_auth(org_id=invitation.from_org_id, one_of_roles=(ADMIN, COORDINATOR, STAFF))

        if invitation.status == InvitationStatus.ACCEPTED.value:
            invitation.is_deleted = True
            invitation.save()
        else:
            invitation.delete()

    @staticmethod
    def _filter_request_invites_role_based(affiliation_invitation_models: List[AffiliationInvitationModel],
                                           org_id: int) -> List[AffiliationInvitationModel]:
        """Filter out affiliation invitations of type REQUEST if current user is not staff or org admin/coordinator."""
        if UserService.is_context_user_staff():
            return affiliation_invitation_models

        if org_id is None:
            return []

        current_user: UserService = UserService.find_by_jwt_token()
        if UserService.is_user_admin_or_coordinator(user=current_user, org_id=org_id):
            return affiliation_invitation_models

        # filter out affiliation invitations of type request
        return list(filter(
            lambda affiliation_invitation: affiliation_invitation.type != AffiliationInvitationType.REQUEST.value,
            affiliation_invitation_models))

    @staticmethod
    def search_invitations(search_filter: AffiliationInvitationSearch, mask_email=True):
        """Search affiliation invitations."""
        try:
            org_id = int(search_filter.to_org_id or search_filter.from_org_id)
        except (TypeError, ValueError):
            org_id = None

        searched_invitations = AffiliationInvitationModel().filter_by(search_filter=search_filter)
        invitation_models = (AffiliationInvitation.
                             _filter_request_invites_role_based(affiliation_invitation_models=searched_invitations,
                                                                org_id=org_id))
        return [AffiliationInvitation(invitation).as_dict(mask_email=mask_email) for invitation in invitation_models]

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
            return AffiliationInvitationModel \
                .filter_by(AffiliationInvitationSearch(to_org_id=org_id, status_codes=['PENDING']))

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
    def _get_app_url(app_url: str, context_path: str = None) -> str:
        """Get app url concatenated with context_path if it exists."""
        full_app_url = app_url
        if context_path:
            full_app_url = f'{full_app_url}/{context_path}'

        return full_app_url

    @staticmethod
    def _get_token_confirm_path(app_url, org_name, token, query_params=None):
        """Get the config for different email types."""
        escape_url = escape_wam_friendly_url(org_name)
        path = f'{escape_url}/affiliationInvitation/acceptToken'
        token_confirm_url = f'{app_url}/{path}/{token}'

        if query_params:
            token_confirm_url += f'?{urlencode(query_params)}'

        return token_confirm_url

    @staticmethod
    def send_affiliation_invitation(affiliation_invitation: AffiliationInvitationModel,
                                    business_name,
                                    app_url=None,
                                    is_authorized=None,
                                    email_addresses=None):
        """Send the email notification."""
        current_app.logger.debug('<send_affiliation_invitation')
        affiliation_invitation_type = affiliation_invitation.type
        from_org_name = affiliation_invitation.from_org.name
        from_org_id = affiliation_invitation.from_org_id
        to_org_name = affiliation_invitation.to_org.name if affiliation_invitation.to_org else None

        data = {
            'accountId': from_org_id,
            'businessName': business_name,
            'emailAddresses': email_addresses,
            'orgName': from_org_name
        }
        notification_type = 'affiliationInvitation'

        if affiliation_invitation_type == AffiliationInvitationType.EMAIL.value:
            # if MAGIC LINK type, add data for magic link
            data['contextUrl'] = AffiliationInvitation._get_token_confirm_path(
                app_url=app_url,
                org_name=from_org_name,
                token=affiliation_invitation.token
            )

        elif affiliation_invitation_type == AffiliationInvitationType.REQUEST.value:
            if not email_addresses:
                # in case that this is old org, and it did not have email, or email was not explicitly provided
                # skip email sending
                return

            # if ACCESS REQUEST type, add data for access request type
            data['fromOrgName'] = affiliation_invitation.from_org.name
            data['toOrgName'] = to_org_name
            if is_authorized is not None:
                notification_type = 'affiliationInvitationRequestAuthorization'
                data['isAuthorized'] = is_authorized
            else:
                notification_type = 'affiliationInvitationRequest'
                data['additionalMessage'] = affiliation_invitation.additional_message

        try:
            publish_to_mailer(notification_type=notification_type, org_id=from_org_id, data=data)
        except BusinessException as exception:
            affiliation_invitation.invitation_status_code = InvitationStatus.FAILED.value
            affiliation_invitation.save()
            current_app.logger.debug('>send_affiliation_invitation failed')
            current_app.logger.debug(exception)
            raise BusinessException(Error.FAILED_AFFILIATION_INVITATION, None) from exception

        current_app.logger.debug('>send_affiliation_invitation')

    @staticmethod
    def send_affiliation_invitation_authorization_email(affiliation_invitation: AffiliationInvitationModel,
                                                        is_authorized: bool):
        """Send authorization email, either for accepted or refused authorization."""
        token = RestService.get_service_account_token(config_id='ENTITY_SVC_CLIENT_ID',
                                                      config_secret='ENTITY_SVC_CLIENT_SECRET')
        business = AffiliationInvitation. \
            _get_business_details(business_identifier=affiliation_invitation.entity.business_identifier,
                                  token=token)
        business_name = business['business']['legalName']

        email_address = AffiliationInvitation. \
            get_invitation_email(affiliation_invitation_type=AffiliationInvitationType.REQUEST,
                                 org_id=affiliation_invitation.from_org_id)

        AffiliationInvitation.send_affiliation_invitation(
            affiliation_invitation=affiliation_invitation,
            business_name=business_name,
            email_addresses=email_address,
            is_authorized=is_authorized
        )

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
        """Add an affiliation from the affiliation invitation."""
        current_app.logger.debug('>accept_affiliation_invitation')
        affiliation_invitation: AffiliationInvitationModel = AffiliationInvitationModel.\
            find_invitation_by_id(affiliation_invitation_id)

        if affiliation_invitation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        if affiliation_invitation.invitation_status_code == InvitationStatus.ACCEPTED.value:
            raise BusinessException(Error.ACTIONED_AFFILIATION_INVITATION, None)
        if affiliation_invitation.invitation_status_code == InvitationStatus.EXPIRED.value:
            raise BusinessException(Error.EXPIRED_AFFILIATION_INVITATION, None)
        if affiliation_invitation.invitation_status_code == InvitationStatus.FAILED.value:
            raise BusinessException(Error.INVALID_AFFILIATION_INVITATION_STATE, None)

        org_id = affiliation_invitation.from_org_id
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

        if affiliation_invitation.type == AffiliationInvitationType.REQUEST.value:
            AffiliationInvitation. \
                send_affiliation_invitation_authorization_email(affiliation_invitation=affiliation_invitation,
                                                                is_authorized=True)

        current_app.logger.debug('<accept_affiliation_invitation')
        return AffiliationInvitation(affiliation_invitation)

    @classmethod
    def get_all_invitations_with_details_related_to_org(cls,
                                                        org_id: int,
                                                        search_filter: AffiliationInvitationSearch) -> List[Dict]:
        """Get affiliation invitations for from org and for to org."""
        affiliation_invitations = AffiliationInvitationModel.find_all_related_to_org(org_id=org_id,
                                                                                     search_filter=search_filter)

        filtered_affiliation_invitations = AffiliationInvitation._filter_request_invites_role_based(
            affiliation_invitation_models=affiliation_invitations, org_id=org_id)

        return cls.affiliation_invitations_to_dict_list(filtered_affiliation_invitations)

    @staticmethod
    def refuse_affiliation_invitation(invitation_id: int, user: UserService):
        """Set affiliation invitation to FAILED state (refusing authorization for affiliation)."""
        invitation: AffiliationInvitationModel = AffiliationInvitationModel.find_invitation_by_id(invitation_id)
        if not invitation:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        if not invitation.status == InvitationStatus.PENDING.value:
            raise BusinessException(Error.INVALID_AFFILIATION_INVITATION_STATE, None)

        invitation.invitation_status_code = InvitationStatus.FAILED.value
        invitation.approver_id = user.identifier
        invitation.save()

        AffiliationInvitation. \
            send_affiliation_invitation_authorization_email(affiliation_invitation=invitation, is_authorized=False)

        return AffiliationInvitation(invitation)
