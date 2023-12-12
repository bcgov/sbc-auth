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
"""Service for managing Affiliation data."""
import datetime
import re
from typing import Dict, List

from flask import current_app
from requests.exceptions import HTTPError
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001
from sqlalchemy.orm import contains_eager, subqueryload

from auth_api.exceptions import BusinessException, ServiceUnavailableException
from auth_api.exceptions.errors import Error
from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.affiliation_invitation import AffiliationInvitation as AffiliationInvitationModel
from auth_api.models.contact_link import ContactLink
from auth_api.models.dataclass import Activity
from auth_api.models.dataclass import Affiliation as AffiliationData
from auth_api.models.dataclass import DeleteAffiliationRequest
from auth_api.models.entity import Entity
from auth_api.models.membership import Membership as MembershipModel
from auth_api.schemas import AffiliationSchema
from auth_api.services.entity import Entity as EntityService
from auth_api.services.org import Org as OrgService
from auth_api.services.user import User as UserService
from auth_api.utils.enums import ActivityAction, CorpType, NRActionCodes, NRNameStatus, NRStatus
from auth_api.utils.passcode import validate_passcode
from auth_api.utils.roles import ALL_ALLOWED_ROLES, CLIENT_AUTH_ROLES, STAFF
from auth_api.utils.user_context import UserContext, user_context
from .activity_log_publisher import ActivityLogPublisher
from .rest_service import RestService


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Affiliation:
    """Manages all aspect of Affiliation data.

    This manages updating, retrieving, and creating Affiliation data via the Affiliation model.
    """

    def __init__(self, model):
        """Return an Affiliation Service."""
        self._model = model

    @property
    def identifier(self):
        """Return the unique identifier for this model."""
        return self._model.id

    @property
    def entity(self):
        """Return the entity for this affiliation as a service."""
        return EntityService(self._model.entity)

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the affiliation as a python dictionary.

        None fields are not included in the dictionary.
        """
        affiliation_schema = AffiliationSchema()
        obj = affiliation_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def find_visible_affiliations_by_org_id(org_id, environment=None):
        """Given an org_id, this will return the entities affiliated with it."""
        current_app.logger.debug(f'<find_visible_affiliations_by_org_id for org_id {org_id}')
        if not org_id:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        org = OrgService.find_by_org_id(org_id, allowed_roles=ALL_ALLOWED_ROLES)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        data = Affiliation.find_affiliations_by_org_id(org_id, environment)

        # 3806 : Filter out the NR affiliation if there is IA affiliation for the same NR.
        # Dict with key as NR number and value as name
        nr_number_name_dict = {d['business_identifier']: d['name']
                               for d in data if d['corp_type']['code'] == CorpType.NR.value}
        # Create a list of all temporary business names
        temp_types = (CorpType.TMP.value, CorpType.RTMP.value)
        tmp_business_list = [d['name'] for d in data if d['corp_type']['code'] in temp_types]

        # NR Numbers
        nr_numbers = nr_number_name_dict.keys()

        filtered_affiliations: list = []
        for entity in data:
            if entity['corp_type']['code'] == CorpType.NR.value:
                # If there is a TMP affiliation present for the NR, do not show NR
                if not entity['business_identifier'] in tmp_business_list:
                    filtered_affiliations.append(entity)

            elif entity['corp_type']['code'] in temp_types:

                # If affiliation is not for a named company IA, and not a Numbered company
                # (name and businessIdentifier same)
                # --> Its a Temp affiliation with incorporation complete.
                # In this case, a TMP affiliation will be there but the name will be BC...
                if entity['name'] in nr_numbers or entity['name'] == entity['business_identifier']:
                    # If temp affiliation is for an NR, change the name to NR's name
                    if entity['name'] in nr_numbers:
                        entity['nr_number'] = entity['name']
                        entity['name'] = nr_number_name_dict[entity['name']]

                    filtered_affiliations.append(entity)
            else:
                filtered_affiliations.append(entity)

        current_app.logger.debug('>find_visible_affiliations_by_org_id')
        return filtered_affiliations

    @staticmethod
    def find_affiliations_by_org_id(org_id, environment=None):
        """Return business affiliations for the org."""
        # Accomplished in service instead of model (easier to avoid circular reference issues).
        entities = db.session.query(Entity) \
            .join(AffiliationModel) \
            .options(
                contains_eager(Entity.affiliations),
                subqueryload(Entity.contacts).subqueryload(ContactLink.contact),
                subqueryload(Entity.created_by),
                subqueryload(Entity.modified_by)) \
            .filter(AffiliationModel.org_id == org_id, Entity.affiliations.any(AffiliationModel.org_id == org_id))
        if environment:
            entities = entities.filter(AffiliationModel.environment == environment)
        else:
            entities = entities.filter(AffiliationModel.environment.is_(None))
        entities = entities.order_by(AffiliationModel.created.desc()).all()
        return [EntityService(entity).as_dict() for entity in entities]

    @staticmethod
    def find_affiliation(org_id, business_identifier, environment=None):
        """Return business affiliation by the org id and business identifier."""
        affiliation = AffiliationModel.find_affiliation_by_org_id_and_business_identifier(org_id,
                                                                                          business_identifier,
                                                                                          environment)
        if affiliation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        return Affiliation(affiliation).as_dict()

    @staticmethod
    def create_affiliation(org_id, business_identifier, environment=None, pass_code=None, certified_by_name=None):
        """Create an Affiliation."""
        # Validate if org_id is valid by calling Org Service.
        current_app.logger.info(f'<create_affiliation org_id:{org_id} business_identifier:{business_identifier}')
        # Security check below.
        org = OrgService.find_by_org_id(org_id, allowed_roles=ALL_ALLOWED_ROLES)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier, skip_auth=True)
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        current_app.logger.debug('<create_affiliation entity found')
        entity_id = entity.identifier
        entity_type = entity.corp_type

        if not Affiliation.is_authorized(entity, pass_code):
            current_app.logger.debug('<create_affiliation not authorized')
            raise BusinessException(Error.INVALID_USER_CREDENTIALS, None)

        current_app.logger.debug('<create_affiliation find affiliation')
        # Ensure this affiliation does not already exist
        affiliation = AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id, entity_id, environment)
        if affiliation is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        affiliation = AffiliationModel(org_id=org_id, entity_id=entity_id, certified_by_name=certified_by_name,
                                       environment=environment)
        affiliation.save()

        if entity_type not in ['SP', 'GP']:
            entity.set_pass_code_claimed(True)
        if entity_type not in [CorpType.RTMP.value, CorpType.TMP.value]:
            name = entity.name if len(entity.name) > 0 else entity.business_identifier
            ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.CREATE_AFFILIATION.value,
                                                           name=name, id=entity.business_identifier))
        return Affiliation(affiliation)

    @staticmethod
    def is_authorized(entity: Entity, pass_code: str) -> bool:
        """Return True if user is authorized to create an affiliation."""
        if Affiliation.is_staff_or_sbc_staff():
            return True
        if entity.corp_type in ['SP', 'GP']:
            if not pass_code:
                return False
            token = RestService.get_service_account_token(config_id='ENTITY_SVC_CLIENT_ID',
                                                          config_secret='ENTITY_SVC_CLIENT_SECRET')
            return Affiliation._validate_firms_party(token, entity.business_identifier, pass_code)
        if pass_code:
            return validate_passcode(pass_code, entity.pass_code)
        if entity.pass_code:
            return False
        return True

    @staticmethod
    def create_new_business_affiliation(affiliation_data: AffiliationData,  # pylint: disable=too-many-locals
                                        environment: str = None):
        """Initiate a new incorporation."""
        org_id = affiliation_data.org_id
        business_identifier = affiliation_data.business_identifier
        email = affiliation_data.email
        phone = affiliation_data.phone
        certified_by_name = affiliation_data.certified_by_name

        current_app.logger.info(f'<create_affiliation org_id:{org_id} business_identifier:{business_identifier}')
        user_is_staff = Affiliation.is_staff_or_sbc_staff()
        if not user_is_staff and (not email and not phone):
            raise BusinessException(Error.NR_INVALID_CONTACT, None)

        # Validate if org_id is valid by calling Org Service.
        org = OrgService.find_by_org_id(org_id, allowed_roles=(*CLIENT_AUTH_ROLES, STAFF))
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier, skip_auth=True)

        # Call the legal-api to verify the NR details
        if not (nr_json := Affiliation._get_nr_details(business_identifier)):
            raise BusinessException(Error.NR_NOT_FOUND, None)

        status = nr_json.get('state')

        if status not in (NRStatus.APPROVED.value, NRStatus.CONDITIONAL.value,
                          NRStatus.DRAFT.value, NRStatus.INPROGRESS.value):
            raise BusinessException(Error.NR_INVALID_STATUS, None)

        if not nr_json.get('applicants'):
            raise BusinessException(Error.NR_INVALID_APPLICANTS, None)

        nr_phone = nr_json.get('applicants').get('phoneNumber')
        nr_email = nr_json.get('applicants').get('emailAddress')

        if status == NRStatus.DRAFT.value:
            invoices = Affiliation.get_nr_payment_details(business_identifier)

            # Ideally there should be only one or two (priority fees) payment request for the NR.
            if not (invoices and invoices['invoices'] and invoices['invoices'][0].get('statusCode') == 'COMPLETED'):
                raise BusinessException(Error.NR_NOT_PAID, None)

        # If consentFlag is not R, N or Null for a CONDITIONAL NR throw error
        if status == NRStatus.CONDITIONAL.value and nr_json.get('consentFlag', None) not in (None, 'R', 'N'):
            raise BusinessException(Error.NR_NOT_APPROVED, None)

        if not user_is_staff and ((phone and re.sub(r'\D', '', phone) != re.sub(r'\D', '', nr_phone)) or
                                  (email and email.casefold() != nr_email.casefold())):
            raise BusinessException(Error.NR_INVALID_CONTACT, None)

        # Create an entity with the Name from NR if entity doesn't exist
        if not entity:
            # Filter the names from NR response and get the name which has status APPROVED as the name.
            # Filter the names from NR response and get the name which has status CONDITION as the name.
            nr_name_state = NRNameStatus.APPROVED.value if status == NRStatus.APPROVED.value \
                else NRNameStatus.CONDITION.value
            name = next((name.get('name') for name in nr_json.get('names') if
                        name.get('state', None) == nr_name_state), None)

            entity = EntityService.save_entity({
                'businessIdentifier': business_identifier,
                'name': name or business_identifier,
                'corpTypeCode': CorpType.NR.value,
                'passCodeClaimed': True
            })

        # Affiliation may already already exist.
        if not (affiliation_model :=
                AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id, entity.identifier, environment)):
            # Create an affiliation with org
            affiliation_model = AffiliationModel(
                org_id=org_id, entity_id=entity.identifier, certified_by_name=certified_by_name)

            if entity.corp_type not in [CorpType.RTMP.value, CorpType.TMP.value]:
                ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.CREATE_AFFILIATION.value,
                                                               name=entity.name, id=entity.business_identifier))
        affiliation_model.certified_by_name = certified_by_name
        affiliation_model.environment = environment
        affiliation_model.save()
        entity.set_pass_code_claimed(True)

        return Affiliation(affiliation_model)

    @staticmethod
    def get_nr_payment_details(business_identifier):
        """Get the NR payment details."""
        pay_api_url = current_app.config.get('PAY_API_URL')
        invoices = RestService.get(
            f'{pay_api_url}/payment-requests?businessIdentifier={business_identifier}',
            token=RestService.get_service_account_token()
        ).json()
        return invoices

    @staticmethod
    def delete_affiliation(delete_affiliation_request: DeleteAffiliationRequest, environment: str = None):
        """Delete the affiliation for the provided org id and business id."""
        org_id = delete_affiliation_request.org_id
        business_identifier = delete_affiliation_request.business_identifier
        reset_passcode = delete_affiliation_request.reset_passcode
        log_delete_draft = delete_affiliation_request.log_delete_draft
        email_addresses = delete_affiliation_request.email_addresses

        current_app.logger.info(f'<delete_affiliation org_id:{org_id} business_identifier:{business_identifier}')
        org = OrgService.find_by_org_id(org_id, allowed_roles=(*CLIENT_AUTH_ROLES, STAFF))
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier,
                                                           allowed_roles=(*CLIENT_AUTH_ROLES, STAFF))
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity_id = entity.identifier

        affiliation = AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id=org_id, entity_id=entity_id,
                                                                              environment=environment)
        if affiliation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        # Could possibly be a single row.
        for affiliation_invitation in AffiliationInvitationModel.find_invitations_by_affiliation(affiliation.id):
            affiliation_invitation.delete()

        if reset_passcode:
            entity.reset_passcode(entity.business_identifier, email_addresses)
        affiliation.delete()
        entity.set_pass_code_claimed(False)

        if entity.corp_type in [CorpType.RTMP.value, CorpType.TMP.value]:
            return

        # When registering a business (also RTMP and TMP in between):
        # 1. affiliate a NR
        # 2. unaffiliate a NR draft
        # 3. affiliate a business (with NR in identifier)
        # 4. unaffilliate a business (with NR in identifier)
        # 5. affilliate a business (with FM or BC in identifier)
        # Users can also intentionally delete a draft. We want to log this action.
        name_request = (entity.status in [NRStatus.DRAFT.value, NRStatus.CONSUMED.value] and
                        entity.corp_type == CorpType.NR.value) or 'NR ' in entity.business_identifier
        publish = log_delete_draft or not name_request
        if publish:
            name = entity.name if len(entity.name) > 0 else entity.business_identifier
            ActivityLogPublisher.publish_activity(Activity(org_id, ActivityAction.REMOVE_AFFILIATION.value,
                                                           name=name, id=entity.business_identifier))

    @staticmethod
    @user_context
    def fix_stale_affiliations(org_id: int, entity_details: Dict, environment: str = None, **kwargs):
        """Corrects affiliations to point at the latest entity."""
        # Example staff/client scenario:
        # 1. client creates an NR (that gets affiliated) - realizes they need help to create a business
        # 2. staff takes NR, creates a business
        # 3. filer updates the business for staff (which creates a new entity)
        # 4. fix_stale_affiliations is called, and fixes the client's affiliation to point at this new entity
        user_from_context: UserContext = kwargs['user_context']
        if not user_from_context.is_system():
            return
        nr_number: str = entity_details.get('nrNumber')
        bootstrap_identifier: str = entity_details.get('bootstrapIdentifier')
        identifier: str = entity_details.get('identifier')
        current_app.logger.debug(f'<fix_stale_affiliations - {nr_number} {bootstrap_identifier} {identifier}')
        from_entity: Entity = EntityService.find_by_business_identifier(nr_number, skip_auth=True)
        # Find entity with nr_number (stale, because this is now a business)
        if from_entity and from_entity.corp_type == 'NR' and \
                (to_entity := EntityService.find_by_business_identifier(identifier, skip_auth=True)):
            affiliations = AffiliationModel.find_affiliations_by_entity_id(from_entity.identifier, environment)
            for affiliation in affiliations:
                # These are already handled by the filer.
                if affiliation.org_id == org_id:
                    continue
                current_app.logger.debug(
                        f'Moving affiliation {affiliation.id} from {from_entity.identifier} to {to_entity.identifier}')
                affiliation.entity_id = to_entity.identifier
                affiliation.environment = environment
                affiliation.save()

        current_app.logger.debug('>fix_stale_affiliations')

    @staticmethod
    async def get_affiliation_details(affiliations: List[AffiliationModel]) -> List:
        """Return affiliation details by calling the source api."""
        url_identifiers = {}  # i.e. turns into { url: [identifiers...] }
        for affiliation in affiliations:
            url = affiliation.affiliation_details_url
            url_identifiers.setdefault(url, [affiliation.entity.business_identifier])\
                .append(affiliation.entity.business_identifier)

        call_info = [{'url': url, 'payload': {'identifiers': identifiers}}
                     for url, identifiers in url_identifiers.items()]

        token = RestService.get_service_account_token(
            config_id='ENTITY_SVC_CLIENT_ID', config_secret='ENTITY_SVC_CLIENT_SECRET')
        try:
            responses = await RestService.call_posts_in_parallel(call_info, token)
            combined = Affiliation._combine_affiliation_details(responses)
            # Should provide us with ascending order
            affiliations_sorted = sorted(affiliations, key=lambda x: x.created, reverse=True)
            # Provide us with a dict with the max created date.
            ordered = {affiliation.entity.business_identifier:
                       affiliation.created for affiliation in affiliations_sorted}

            def sort_key(item):
                identifier = item.get('identifier', item.get('nameRequest', {}).get('nrNum', ''))
                return ordered.get(identifier, datetime.datetime.min)

            combined.sort(key=sort_key, reverse=True)

            return combined
        except ServiceUnavailableException as err:
            current_app.logger.debug(err)
            current_app.logger.debug('Failed to get affiliations details: %s', affiliations)
            raise ServiceUnavailableException('Failed to get affiliation details') from err

    @staticmethod
    def _combine_affiliation_details(details):
        """Parse affiliation details responses and combine draft entities with NRs if applicable."""
        name_requests = {}
        businesses = []
        drafts = []
        businesses_key = 'businessEntities'
        drafts_key = 'draftEntities'
        for data in details:
            if isinstance(data, list):
                # assume this is an NR list
                for name_request in data:
                    # i.e. {'NR1234567': {...}}
                    name_requests[name_request['nrNum']] = {'legalType': CorpType.NR.value, 'nameRequest': name_request}
                continue
            if businesses_key in data:
                businesses = list(data[businesses_key])
            if drafts_key in data:
                # set draft type so that UI knows its a draft entity
                draft_reg_types = [CorpType.GP.value, CorpType.SP.value]
                drafts = [
                    {'draftType': CorpType.RTMP.value if draft['legalType'] in draft_reg_types
                        else CorpType.TMP.value, **draft} for draft in data[drafts_key]]

        # combine NRs
        for business in drafts + businesses:
            # Only drafts have nrNumber coming back from legal-api.
            if 'nrNumber' in business and (nr_num := business['nrNumber']):
                if business['nrNumber'] in name_requests:
                    business['nameRequest'] = name_requests[nr_num]['nameRequest']
                    # Update the draft type if the draft NR request is for amalgamation
                    if business.get('draftType', None) \
                            and business['nameRequest']['request_action_cd'] == NRActionCodes.AMALGAMATE.value:
                        business['draftType'] = CorpType.ATMP.value
                    # Remove the business if the draft associated to the NR is consumed.
                    if business['nameRequest']['stateCd'] == NRStatus.CONSUMED.value:
                        drafts.remove(business)
                    del name_requests[nr_num]
                else:
                    # If not in name_requests then it's a stale draft.
                    drafts.remove(business)

        return [name_request for nr_num, name_request in name_requests.items()] + drafts + businesses

    @staticmethod
    def _get_nr_details(nr_number: str):
        """Return NR details by calling legal-api."""
        nr_api_url = current_app.config.get('NAMEX_API_URL')
        get_nr_url = f'{nr_api_url}/requests/{nr_number}'
        try:
            token = RestService.get_service_account_token(
                config_id='ENTITY_SVC_CLIENT_ID', config_secret='ENTITY_SVC_CLIENT_SECRET')
            get_nr_response = RestService.get(get_nr_url, token=token, skip_404_logging=True)
        except (HTTPError, ServiceUnavailableException) as e:
            current_app.logger.info(e)
            raise BusinessException(Error.DATA_NOT_FOUND, None) from e

        return get_nr_response.json()

    @staticmethod
    def _validate_firms_party(token, business_identifier, party_name_str: str):
        legal_api_url = current_app.config.get('LEGAL_API_URL') + current_app.config.get('LEGAL_API_VERSION_2')
        parties_url = f'{ legal_api_url }/businesses/{business_identifier}/parties'
        try:
            lear_response = RestService.get(parties_url, token=token, skip_404_logging=True)
        except (HTTPError, ServiceUnavailableException) as e:
            current_app.logger.info(e)
            raise BusinessException(Error.DATA_NOT_FOUND, None) from e
        parties_json = lear_response.json()
        for party in parties_json['parties']:
            officer = party.get('officer')
            if officer.get('partyType') == 'organization':
                party_name = officer.get('organizationName')
            else:
                party_name = officer.get('lastName') + ', ' + officer.get('firstName')
                if officer.get('middleInitial'):
                    party_name = party_name + ' ' + officer.get('middleInitial')

            # remove duplicate spaces
            party_name_str = ' '.join(party_name_str.split())
            party_name = ' '.join(party_name.split())

            if party_name_str.upper() == party_name.upper():
                return True
        return False

    @staticmethod
    @user_context
    def is_staff_or_sbc_staff(**kwargs):
        """Return True if user is staff or sbc staff."""
        user_from_context: UserContext = kwargs['user_context']
        current_user: UserService = UserService.find_by_jwt_token(silent_mode=True)
        if user_from_context.is_staff() or \
           (current_user and MembershipModel.check_if_sbc_staff(current_user.identifier)):
            return True
        return False
