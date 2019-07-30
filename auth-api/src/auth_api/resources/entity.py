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
"""API endpoints for managing an entity (business) resource."""

from flask_restplus import Namespace, Resource

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.services.entity import Entity as EntityService
from auth_api.tracer import Tracer
from auth_api.utils.util import cors_preflight


API = Namespace('entities', description='Entities')
TRACER = Tracer.get_instance()


@cors_preflight('GET, POST, PUT')
@API.route('/<string:business_identifier>', methods=['GET'])
class EntityResource(Resource):
    """Resource for managing entities."""

    @staticmethod
    @TRACER.trace()
    def get(business_identifier):
        """Get an existing entity by it's business number."""
        try:
            response, status = EntityService.find_by_business_identifier(business_identifier).as_dict(), \
                http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status
