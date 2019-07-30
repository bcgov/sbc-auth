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
"""Service for managing Entity data."""

from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import Entity as EntityModel
from auth_api.models import EntitySchema


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Entity:
    """Manages all aspect of Entity data.

    This manages updating, retrieving, and creating Entity data via the Entity model.
    """

    def __init__(self, model):
        """Return an Entity Service."""
        self._model = model

    @property
    def business_identifier(self):
        """Return the business identifier for this Entity."""
        return self._model.business_identifier

    @business_identifier.setter
    def business_identifier(self, value: str):
        """Set the business identifier for this Entity."""
        self._model.business_identifier = value

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the entity as a python dictionary.

        None fields are not included in the dictionary.
        """
        entity_schema = EntitySchema()
        dict_obj = entity_schema.dump(self._model)
        return dict_obj

    @classmethod
    def find_by_business_identifier(cls, business_identifier: str = None):
        """Given a business identifier, this will return the corresponding entity or None."""
        if not business_identifier:
            return None

        entity_model = EntityModel.find_by_business_identifier(business_identifier)

        if not entity_model:
            raise BusinessException(Error.DATA_NOT_FOUND, None)

        entity = Entity(entity_model)
        return entity
