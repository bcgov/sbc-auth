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

from typing import Dict

from flask import current_app
from requests.exceptions import HTTPError
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.exceptions import BusinessException
from auth_api.exceptions import ServiceUnavailableException
from auth_api.exceptions.errors import Error
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.schemas import AffiliationSchema
from auth_api.services.entity import Entity as EntityService
from auth_api.services.org import Org as OrgService
from auth_api.utils.enums import CorpType
from auth_api.utils.passcode import validate_passcode
from auth_api.utils.roles import ALL_ALLOWED_ROLES, CLIENT_AUTH_ROLES, STAFF
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
    def find_affiliated_entities_by_org_id(org_id, token_info: Dict = None):
        """Given an org_id, this will return the entities affiliated with it."""
        current_app.logger.debug('<find_affiliations_by_org_id for org_id {}'.format(org_id))
        if not org_id:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        org = OrgService.find_by_org_id(org_id, token_info=token_info, allowed_roles=ALL_ALLOWED_ROLES)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        data = []
        affiliation_models = AffiliationModel.find_affiliations_by_org_id(org_id)
        if affiliation_models is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        for affiliation_model in affiliation_models:
            data.append(EntityService(affiliation_model.entity).as_dict())

        # 3806 : Filter out the NR affiliation if there is IA affiliation for the same NR.
        tmp_business_list = [d['name'] for d in data if d['corpType']['code'] == CorpType.TMP.value]
        data = list(filter(lambda affiliation: (affiliation['businessIdentifier'] not in tmp_business_list), data))

        current_app.logger.debug('>find_affiliations_by_org_id')

        return data

    @staticmethod
    def create_affiliation(org_id, business_identifier, pass_code=None, token_info: Dict = None):
        """Create an Affiliation."""
        # Validate if org_id is valid by calling Org Service.
        current_app.logger.info(f'<create_affiliation org_id:{org_id} business_identifier:{business_identifier}')
        org = OrgService.find_by_org_id(org_id, token_info=token_info, allowed_roles=CLIENT_AUTH_ROLES)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier, skip_auth=True)
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)
        current_app.logger.debug('<create_affiliation entity found')
        entity_id = entity.identifier

        authorized = True
        already_claimed = False

        # Authorized if the entity has been claimed
        if entity.as_dict()['passCodeClaimed']:
            authorized = False
            already_claimed = True

        # If a passcode was provided...
        elif pass_code:
            # ... and the entity has a passcode on it, check that they match
            authorized = validate_passcode(pass_code, entity.pass_code)
        # If a passcode was not provided...
        else:
            # ... check that the entity does not have a passcode protecting it
            if entity.pass_code:
                authorized = False

        if not authorized:
            # show a different message when the passcode is already claimed
            if already_claimed:
                current_app.logger.debug('<create_affiliation passcode already claimed')
                raise BusinessException(Error.ALREADY_CLAIMED_PASSCODE, None)
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

        return Affiliation(affiliation)

    @staticmethod
    def create_new_business_affiliation(org_id, business_identifier=None,  # pylint: disable=too-many-arguments
                                        email=None, phone=None, token_info: Dict = None, bearer_token: str = None):
        """Initiate a new incorporation."""
        # Validate if org_id is valid by calling Org Service.
        current_app.logger.info(f'<create_affiliation org_id:{org_id} business_identifier:{business_identifier}')
        affiliation_model = None

        if not email and not phone:
            raise BusinessException(Error.NR_INVALID_CONTACT, None)

        org = OrgService.find_by_org_id(org_id, token_info=token_info, allowed_roles=CLIENT_AUTH_ROLES)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier, skip_auth=True)
        # If entity already exists and is already affiliated to an org, throw error
        if entity and entity.as_dict()['passCodeClaimed']:
            raise BusinessException(Error.NR_CONSUMED, None)

        # Call the legal-api to verify the NR details
        nr_json = Affiliation._get_nr_details(business_identifier, bearer_token)

        if nr_json:
            status = nr_json.get('state')
            nr_phone = nr_json.get('applicants').get('phoneNumber')
            nr_email = nr_json.get('applicants').get('emailAddress')

            if status not in ('APPROVED', 'CONDITIONAL'):
                raise BusinessException(Error.NR_NOT_APPROVED, None)

            if (phone and phone != nr_phone) or (email and email != nr_email):
                raise BusinessException(Error.NR_INVALID_CONTACT, None)

            # Create an entity with the Name from NR if entity doesn't exist
            if not entity:
                # Filter the names from NR response and get the name which has status APPROVED as the name.
                name = next(
                    (name.get('name') for name in nr_json.get('names') if name.get('state', None) == 'APPROVED'), None)
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
    def delete_affiliation(org_id, business_identifier, token_info: Dict = None):
        """Delete the affiliation for the provided org id and business id."""
        current_app.logger.info(f'<delete_affiliation org_id:{org_id} business_identifier:{business_identifier}')
        org = OrgService.find_by_org_id(org_id, token_info=token_info, allowed_roles=(*CLIENT_AUTH_ROLES, STAFF))
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier, token_info=token_info,
                                                           allowed_roles=(*CLIENT_AUTH_ROLES, STAFF))
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity_id = entity.identifier

        affiliation = AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id=org_id, entity_id=entity_id)
        if affiliation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        affiliation.delete()
        entity.set_pass_code_claimed(False)

    @staticmethod
    def _get_nr_details(nr_number: str, token: str):
        """Return NR details by calling legal-api."""
        get_nr_url = current_app.config.get('LEGAL_API_URL') + f'/nameRequests/{nr_number}'
        try:
            get_nr_response = RestService.get(get_nr_url, token=token)
        except (HTTPError, ServiceUnavailableException) as e:
            current_app.logger.info(e)
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        return get_nr_response.json()
