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
"""The Authentication service.

This module manages the Authentication information for a user or entity.
"""

from sbc_common_components.tracing.service_tracing import ServiceTracing

from auth_api.schemas import AuthenticationSchemaPublic


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Authentication:
    """Manage all aspects of the Authentication entity."""

    def __init__(self, model):
        """Return a Authentication service object."""
        self._model = model

    @property
    def identifier(self):
        """Return the identifier for this authentication."""
        return self._model.id

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the Authentication as a python dict.

        None fields are not included in the dict.
        """
        authentication_schema = AuthenticationSchemaPublic()
        obj = authentication_schema.dump(self._model, many=False)
        return obj
