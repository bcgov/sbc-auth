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
"""API endpoints for managing a notify resource."""

from flask_restplus import Namespace, Resource, cors

from notify_api import status as http_status
from notify_api.jwt_wrapper import JWTWrapper
from notify_api.tracer import Tracer
from notify_api.utils.util import cors_preflight


API = Namespace('notify', description='Endpoints for notify services')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class Notify(Resource):
    """Resource for notify service."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def post():
        """Send a new notify using the details in request and saves the notify."""
        return {}, http_status.HTTP_200_OK

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def get():
        """Return a set of users based on search query parameters (staff only)."""
        return {}, http_status.HTTP_200_OK
