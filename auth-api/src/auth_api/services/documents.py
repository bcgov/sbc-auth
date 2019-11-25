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
"""Service for managing the documents."""

from jinja2 import Environment, FileSystemLoader

from auth_api.models import Documents as DocumentsModel
from auth_api.schemas import DocumentSchema
from config import get_named_config
from sbc_common_components.tracing.service_tracing import ServiceTracing


ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)
CONFIG = get_named_config()


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class Documents:
    """Manages the documents in DB.

    This service manages retrieving the documents.
    """

    def __init__(self, model):
        """Return an invitation service instance."""
        self._model = model

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the User as a python dict.

        None fields are not included in the dict.
        """
        document_schema = DocumentSchema()
        obj = document_schema.dump(self._model, many=False)
        return obj

    @classmethod
    def fetch_latest_document(cls, document_type):
        """Get a membership type by the given code."""
        doc = DocumentsModel.fetch_latest_document_by_type(file_type=document_type)
        if doc:
            return Documents(doc)
        return None
