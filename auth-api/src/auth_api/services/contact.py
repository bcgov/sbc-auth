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
"""The Contact service.

This module manages the Contact information for a user or entity.
"""

from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001, I003, I004

from auth_api.schemas import ContactSchema, ContactSchemaPublic  # noqa: I001, I003, I004


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Contact:
    """Manage all aspects of the Contact entity."""

    def __init__(self, model):
        """Return a Contact service object."""
        self._model = model

    @property
    def identifier(self):
        """Return the identifier for this contact."""
        return self._model.id

    @ServiceTracing.disable_tracing
    def as_dict(self, masked_email_only=False):
        """Return the Contact as a python dict.

        None fields are not included in the dict.
        """
        contact_schema = ContactSchemaPublic() if masked_email_only else ContactSchema()
        obj = contact_schema.dump(self._model, many=False)
        return obj
