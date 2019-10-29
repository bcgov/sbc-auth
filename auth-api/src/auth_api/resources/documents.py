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
"""API endpoints for managing an Invitation resource."""

from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.services import Documents as DocumentService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight


API = Namespace('invitations', description='Endpoints for invitations management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,OPTIONS')
@API.route('/<string:document_type>', methods=['GET', 'OPTIONS'])
class Documents(Resource):
    """Resource for managing Terms Of Use."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(document_type):
        """Return the latest terms of use."""
        try:
            doc = DocumentService.fetch_terms_of_use_document(document_type)
            if doc is not None:
                response, status = doc.as_dict(), http_status.HTTP_200_OK
            else:
                response, status = {'message': 'The requested invitation could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status
