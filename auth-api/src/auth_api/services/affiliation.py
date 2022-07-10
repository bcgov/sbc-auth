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
"""Service for managing Affiliation data."""

from flask import current_app
from requests.exceptions import HTTPError
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException, ServiceUnavailableException
from auth_api.exceptions.errors import Error
from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.entity import Entity
from auth_api.schemas import AffiliationSchema
from auth_api.services.entity import Entity as EntityService
from auth_api.services.org import Org as OrgService
from auth_api.utils.enums import ActivityAction, CorpType, NRNameStatus, NRStatus
from auth_api.utils.passcode import validate_passcode
from auth_api.utils.roles import ALL_ALLOWED_ROLES, CLIENT_AUTH_ROLES, STAFF
from .activity_log_publisher import publish_activity
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
    def find_visible_affiliations_by_org_id(org_id):
        """Given an org_id, this will return the entities affiliated with it."""
        current_app.logger.debug(f'<find_visible_affiliations_by_org_id for org_id {org_id}')
        if not org_id:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        org = OrgService.find_by_org_id(org_id, allowed_roles=ALL_ALLOWED_ROLES)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        data = Affiliation.find_affiliations_by_org_id(org_id)

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
    def find_affiliations_by_org_id(org_id):
        """Return business affiliations for the org."""
        # Done in service instead of model (easier to avoid circular reference issues).
        entity_ids = db.session.query(AffiliationModel.entity_id) \
            .join(Entity).filter(AffiliationModel.org_id == org_id) \
            .order_by(AffiliationModel.created.desc()) \
            .subquery()

        entities = db.session.query(Entity).filter(Entity.id.in_(entity_ids)).all()
        return [EntityService(entity).as_dict() for entity in entities]

    @staticmethod
    def create_affiliation(org_id, business_identifier, pass_code=None):
        """Create an Affiliation."""
        # Validate if org_id is valid by calling Org Service.
        current_app.logger.info(f'<create_affiliation org_id:{org_id} business_identifier:{business_identifier}')
        org = OrgService.find_by_org_id(org_id, allowed_roles=ALL_ALLOWED_ROLES)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier, skip_auth=True)
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        current_app.logger.debug('<create_affiliation entity found')
        entity_id = entity.identifier

        authorized = True

        # Unauthorized if the entity has been claimed
        # Leaving the code as it may come back. Removing as part of #8863
        # if entity.as_dict()['pass_code_claimed']:
        #     authorized = False
        #     already_claimed = True
        # If a passcode was provided...
        if pass_code:
            # ... and the entity has a passcode on it, check that they match
            authorized = validate_passcode(pass_code, entity.pass_code)
        # If a passcode was not provided...
        else:
            # ... check that the entity does not have a passcode protecting it
            if entity.pass_code:
                authorized = False

        # show a different message when the passcode is already claimed
        # if already_claimed:
        #     current_app.logger.debug('<create_affiliation passcode already claimed')
        #     raise BusinessException(Error.ALREADY_CLAIMED_PASSCODE, None)

        if not authorized:
            current_app.logger.debug('<create_affiliation not authorized')
            raise BusinessException(Error.INVALID_USER_CREDENTIALS, None)

        current_app.logger.debug('<create_affiliation find affiliation')
        # Ensure this affiliation does not already exist
        affiliation = AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id, entity_id)
        if affiliation is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        affiliation = AffiliationModel(org_id=org_id, entity_id=entity_id)
        affiliation.save()

        entity.set_pass_code_claimed(True)
        publish_activity(f'{ActivityAction.CREATE_AFFILIATION.value}-{entity.name}', entity.name, entity_id, org_id)
        return Affiliation(affiliation)

    @staticmethod
    def create_new_business_affiliation(org_id,  # pylint: disable=too-many-arguments, too-many-locals
                                        business_identifier=None, email=None, phone=None,
                                        bearer_token: str = None):
        """Initiate a new incorporation."""
        current_app.logger.info(f'<create_affiliation org_id:{org_id} business_identifier:{business_identifier}')

        if not email and not phone:
            raise BusinessException(Error.NR_INVALID_CONTACT, None)

        # Validate if org_id is valid by calling Org Service.
        org = OrgService.find_by_org_id(org_id, allowed_roles=CLIENT_AUTH_ROLES)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier, skip_auth=True)
        # If entity already exists and passcode is already claimed, throw error
        if entity and entity.as_dict()['pass_code_claimed']:
            raise BusinessException(Error.NR_CONSUMED, None)

        # Call the legal-api to verify the NR details
        nr_json = Affiliation._get_nr_details(business_identifier, bearer_token)

        if nr_json:
            status = nr_json.get('state')
            nr_phone = nr_json.get('applicants').get('phoneNumber')
            nr_email = nr_json.get('applicants').get('emailAddress')

            if status not in (NRStatus.APPROVED.value, NRStatus.CONDITIONAL.value):
                raise BusinessException(Error.NR_NOT_APPROVED, None)

            # If consentFlag is not R, N or Null for a CONDITIONAL NR throw error
            if status == NRStatus.CONDITIONAL.value and nr_json.get('consentFlag', None) not in (None, 'R', 'N'):
                raise BusinessException(Error.NR_NOT_APPROVED, None)

            if (phone and phone != nr_phone) or (email and email.casefold() != nr_email.casefold()):
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
                    'name': name,
                    'corpTypeCode': CorpType.NR.value,
                    'passCodeClaimed': True
                })
            # Create an affiliation with org
            affiliation_model = AffiliationModel(org_id=org_id, entity_id=entity.identifier)
            affiliation_model.save()
            entity.set_pass_code_claimed(True)
        else:
            raise BusinessException(Error.NR_NOT_FOUND, None)

        return Affiliation(affiliation_model)

    @staticmethod
    def delete_affiliation(org_id, business_identifier, email_addresses: str = None,
                           reset_passcode: bool = False):
        """Delete the affiliation for the provided org id and business id."""
        current_app.logger.info(f'<delete_affiliation org_id:{org_id} business_identifier:{business_identifier}')
        org = OrgService.find_by_org_id(org_id, allowed_roles=(*CLIENT_AUTH_ROLES, STAFF))
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier,
                                                           allowed_roles=(*CLIENT_AUTH_ROLES, STAFF))
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity_id = entity.identifier

        affiliation = AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id=org_id, entity_id=entity_id)
        if affiliation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        if reset_passcode:
            entity.reset_passcode(entity.business_identifier, email_addresses)
        affiliation.delete()
        entity.set_pass_code_claimed(False)
        publish_activity(f'{ActivityAction.REMOVE_AFFILIATION.value}-{entity.name}', entity.name,
                         business_identifier, org_id)

    @staticmethod
    def _get_nr_details(nr_number: str, token: str):
        """Return NR details by calling legal-api."""
        get_nr_url = current_app.config.get('LEGAL_API_URL') + f'/nameRequests/{nr_number}'
        try:
            get_nr_response = RestService.get(get_nr_url, token=token)
        except (HTTPError, ServiceUnavailableException) as e:
            current_app.logger.info(e)
            raise BusinessException(Error.DATA_NOT_FOUND, None) from e

        return get_nr_response.json()
