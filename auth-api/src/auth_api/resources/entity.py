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

from flask import g, request
from flask_restplus import Namespace, Resource, cors
from sqlalchemy import exc

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.schemas import utils as schema_utils
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.services.entity import Entity as EntityService
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight


API = Namespace('entities', description='Entities')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class EntityResources(Resource):
    """Resource for managing entities."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def post():
        """Post a new Entity using the request body."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'entity')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            response, status = EntityService.create_entity(request_json).as_dict(), http_status.HTTP_201_CREATED
        except exc.IntegrityError:
            response, status = {'message': 'Business with specified identifier already exists.'}, \
                               http_status.HTTP_409_CONFLICT
        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/<string:business_identifier>', methods=['GET', 'OPTIONS'])
class EntityResource(Resource):
    """Resource for managing entities."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(business_identifier):
        """Get an existing entity by it's business number."""
        try:
            entity = EntityService.find_by_business_identifier(business_identifier)
            if entity is not None:
                response, status = entity.as_dict(), http_status.HTTP_200_OK
            else:
                response, status = {'message': 'A business for {} was not found.'.format(business_identifier)}, \
                                   http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('DELETE,POST,PUT,OPTIONS')
@API.route('/<string:business_identifier>/contacts', methods=['DELETE', 'POST', 'PUT', 'OPTIONS'])
class ContactResource(Resource):
    """Resource for managing entity contacts."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @cors.crossdomain(origin='*')
    def post(business_identifier):
        """Add a new contact for the Entity identified by the provided id."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            entity = EntityService.find_by_business_identifier(business_identifier)
            if entity:
                response, status = entity.add_contact(request_json).as_dict(), \
                                   http_status.HTTP_201_CREATED
            else:
                response, status = {'message': 'The requested business could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @cors.crossdomain(origin='*')
    def put(business_identifier):
        """Update the business contact for the Entity identified by the provided id."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            entity = EntityService.find_by_business_identifier(business_identifier)
            if entity:
                response, status = entity.update_contact(request_json).as_dict(), \
                                   http_status.HTTP_200_OK
            else:
                response, status = {'message': 'The requested business could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @cors.crossdomain(origin='*')
    def delete(business_identifier):
        """Delete the business contact for the Entity identified by the provided id."""
        try:
            entity = EntityService.find_by_business_identifier(business_identifier)
            if entity:
                response, status = entity.delete_contact().as_dict(), http_status.HTTP_200_OK
            else:
                response, status = {'message': 'The requested business could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,OPTIONS')
@API.route('/<string:business_identifier>/authorizations', methods=['GET', 'OPTIONS'])
class AuthorizationResource(Resource):
    """Resource for managing entity authorizations."""

    @staticmethod
    @_JWT.requires_auth
    @cors.crossdomain(origin='*')
    def get(business_identifier):
        """Return authorization for the user for the passed business identifier."""
        authorisations = AuthorizationService.get_user_authorizations_for_entity(g.jwt_oidc_token_info,
                                                                                 business_identifier)
        return authorisations, http_status.HTTP_200_OK
