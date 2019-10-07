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

from flask import request
from flask_restplus import Namespace, Resource, cors

from notify_api import status as http_status
from notify_api.jwt_wrapper import JWTWrapper
from notify_api.schemas import utils as schema_utils
from notify_api.services import Notify as NotifyService
from notify_api.tracer import Tracer
from notify_api.utils.util import cors_preflight


API = Namespace('notify', description='Endpoints for notify services')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class Notify(Resource):
    """Resource for notify (POST) service."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def post():
        """Send a new notification using the details in request and saves the notification."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'notify')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        notification = NotifyService.create_notification(request_json)
        if notification is None:
            response, status = {'message': 'Service Error.'}, http_status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            response, status = notification.as_dict(), http_status.HTTP_201_CREATED
        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/<string:notification_id>', methods=['GET'])
class Notification(Resource):
    """Resource for notify (GET) service."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def get(notification_id):
        """Get the notification specified by the provided id."""
        notification = NotifyService.get_notification(notification_id)
        if notification is None or not notification.as_dict():
            response, status = {'message': 'The requested notification could not be found.'}, \
                http_status.HTTP_404_NOT_FOUND
        else:
            response, status = notification.as_dict(), http_status.HTTP_200_OK
        return response, status
