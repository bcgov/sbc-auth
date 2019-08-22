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

from typing import Any, Dict
from flask import current_app
from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.schemas import AffiliationSchema
from auth_api.services.org import Org as OrgService
from auth_api.services.entity import Entity as EntityService


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Affiliation:
    """Manages all aspect of Affiliation data.

    This manages updating, retrieving, and creating Affiliation data via the Affiliation model.
    """

    def __init__(self, model):
        """Return an Affiliation Service."""
        self._model = model

    @property
    def id(self):
        """Return the id for this Affiliation."""
        return self._model.id

    @id.setter
    def id(self, value: int):
        """Set the id for this Affiliation."""
        self._model.id = value

    @property
    def created_by(self):
        """Return the create_by for this Affiliation."""
        return self._model.created_by

    @created_by.setter
    def created_by(self, value: int):
        """Set the create_by for this Affiliation."""
        self._model.created_by = value

    @property
    def entity(self):
        """Return the entity for this Affiliation."""
        return self._model.entity

    @entity.setter
    def entity(self, value: int):
        """Set the entity for this Affiliation."""
        self._model.entity = value

    @property
    def org(self):
        """Return the org for this Affiliation."""
        return self._model.org

    @org.setter
    def org(self, value: int):
        """Set the org for this Affiliation."""
        self._model.org = value

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the affiliation as a python dictionary.

        None fields are not included in the dictionary.
        """
        affiliation_schema = AffiliationSchema()
        obj = affiliation_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    def find_affiliation_by_ids(org_id, affiliation_id):
        """Given an org_id and affiliation_id, this will return the corresponding affiliation or None."""
        if not org_id or not affiliation_id:
            return None

        affiliation_model = AffiliationModel.find_affiliation_by_ids(org_id, affiliation_id)

        if not affiliation_model:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        return Affiliation(affiliation_model).as_dict()

    @staticmethod
    def find_affiliations_by_org_id(org_id):
        """Given an org_id, this will return the corresponding affiliations or None."""
        current_app.logger.debug('<find_affiliations_by_org_id for org_id {}'.format(org_id))
        if not org_id:
            return None

        org = OrgService.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        data = {'items': []}
        affiliation_models = AffiliationModel.find_affiliations_by_org_id(int(org_id))
        if affiliation_models is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        for affiliation_model in affiliation_models:
            if affiliation_model:
                data['items'].append(Affiliation(affiliation_model).as_dict())
        current_app.logger.debug('>find_affiliations_by_org_id')

        return data

    @staticmethod
    def create_affiliation(org_id, entity_info: Dict[str, Any]):
        """Create an Affiliation."""

        # Validate if org_id is valid by calling Org Service.
        org = OrgService.find_by_org_id(org_id)
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_entity_id(entity_info.get('entity'))
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        affiliation = AffiliationModel()
        affiliation.entity = entity.as_dict()['id']
        affiliation.org = org_id

        affiliation.save()
        affiliation = Affiliation(affiliation)

        return affiliation.as_dict()

    @staticmethod
    def update_affiliation(org_id, affiliation_id, entity_info: Dict[str, Any]):
        """Update an Affiliation."""
        affiliation = AffiliationModel.find_by_affiliation_id(int(affiliation_id))
        if affiliation is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        org = OrgService.find_by_org_id(int(org_id))
        if org is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = EntityService.find_by_entity_id(int(entity_info.get('entity')))
        if entity is None:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        affiliation.entity = int(entity_info.get('entity'))
        affiliation.org = int(org_id)
        affiliation.save()
        affiliation = Affiliation(affiliation)
        return affiliation
