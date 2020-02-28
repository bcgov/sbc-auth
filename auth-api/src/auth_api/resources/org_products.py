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
"""API endpoints for managing an Org resource."""

from flask import g, jsonify, request
from flask_restplus import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.schemas import ProductSubscriptionSchema
from auth_api.schemas import utils as schema_utils
from auth_api.services import Invitation as InvitationService
from auth_api.services import Membership as MembershipService
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.enums import NotificationType
from auth_api.utils.roles import ALL_ALLOWED_ROLES, CLIENT_ADMIN_ROLES, MEMBER, Role, Status
from auth_api.utils.util import cors_preflight

API = Namespace('orgs', description='Endpoints for organization products management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class OrgProducts(Resource):
    """Resource for managing a user's settings."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.STAFF_ADMIN.value])
    def post(org_id):
        """Post a new product subscription to the org using the request body.
        """
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'org_product_subscription')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST


        try:
            subscriptions = OrgService.create_product_subscription(request_json, org_id)
            if subscriptions is None:
                response, status = {'message': 'Not authorized to perform this action'}, \
                                   http_status.HTTP_401_UNAUTHORIZED
            else:
                response, status = {'subscriptions': ProductSubscriptionSchema().dump(subscriptions, many=True)}, \
                                   http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status
