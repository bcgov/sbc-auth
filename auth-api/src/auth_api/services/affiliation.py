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
from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.schemas import AffiliationSchema
from auth_api.services.entity import Entity as EntityService
from auth_api.services.org import Org as OrgService


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
    def find_affiliated_entities_by_org_id(org_id):
        """Given an org_id, this will return the entities affiliated with it."""
        current_app.logger.debug('<find_affiliations_by_org_id for org_id {}'.format(org_id))
        if not org_id:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        org = OrgService.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        data = []
        affiliation_models = AffiliationModel.find_affiliations_by_org_id(org_id)
        if affiliation_models is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        for affiliation_model in affiliation_models:
            if affiliation_model:
                data.append(EntityService(affiliation_model.entity).as_dict())
        current_app.logger.debug('>find_affiliations_by_org_id')

        return data

    @staticmethod
    def create_affiliation(org_id, business_identifier, pass_code=None):
        """Create an Affiliation."""
        # Validate if org_id is valid by calling Org Service.
        org = OrgService.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier)
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity_id = entity.identifier

        authorized = True

        # Authorized if the entity has been claimed
        if entity.as_dict()['passCodeClaimed']:
            authorized = False

        # If a passcode was provided...
        if pass_code:
            # ... and the entity has a passcode on it, check that they match
            if entity.pass_code != pass_code:
                authorized = False
        # If a passcode was not provided...
        else:
            # ... check that the entity does not have a passcode protecting it
            if entity.pass_code:
                authorized = False

        if not authorized:
            # If org being affiliated was IMPLICIT, remove it since the affiliation was not valid
            if org.as_dict()['org_type'] == 'IMPLICIT':
                org.delete_org()
            raise BusinessException(Error.INVALID_USER_CREDENTIALS, None)

        # Ensure this affiliation does not already exist
        affiliation = AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id, entity_id)
        if affiliation is not None:
            raise BusinessException(Error.DATA_ALREADY_EXISTS, None)

        affiliation = AffiliationModel(org_id=org_id, entity_id=entity_id)
        affiliation.save()
        entity.set_pass_code_claimed(True)

        return Affiliation(affiliation)

    @staticmethod
    def delete_affiliation(org_id, business_identifier):
        """Delete the affiliation for the provided org id and business id."""
        org = OrgService.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_business_identifier(business_identifier)
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity_id = entity.identifier

        affiliation = AffiliationModel.find_affiliation_by_org_and_entity_ids(org_id=org_id, entity_id=entity_id)
        if affiliation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        affiliation.delete()
        entity.set_pass_code_claimed(False)
