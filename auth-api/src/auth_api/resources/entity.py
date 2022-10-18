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

from flask import request
from flask_restx import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import Affiliation as AffiliationService
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.services.entity import Entity as EntityService
from auth_api.tracer import Tracer
from auth_api.utils.roles import ALL_ALLOWED_ROLES, CLIENT_AUTH_ROLES, Role
from auth_api.utils.util import cors_preflight


API = Namespace('entities', description='Entities')
TRACER = Tracer.get_instance()


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class EntityResources(Resource):
    """Resource for managing entities."""

    @staticmethod
    @_jwt.has_one_of_roles([Role.SYSTEM.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def post():
        """Post a new Entity using the request body."""
        request_json = request.get_json()

        # If the record exists, just return existing record.
        entity = EntityService.find_by_business_identifier(request_json.get('businessIdentifier'),
                                                           allowed_roles=ALL_ALLOWED_ROLES)
        if entity:
            return entity.as_dict(), http_status.HTTP_202_ACCEPTED

        valid_format, errors = schema_utils.validate(request_json, 'entity')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            details = request_json.pop('details', None)
            entity = EntityService.save_entity(request_json)
            if details:
                AffiliationService.fix_stale_affiliations(details)
            response, status = entity.as_dict(), http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,OPTIONS,PATCH,DELETE')
@API.route('/<string:business_identifier>', methods=['GET', 'OPTIONS', 'PATCH', 'DELETE'])
class EntityResource(Resource):
    """Resource for managing entities."""

    @staticmethod
    @_jwt.requires_auth
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(business_identifier):
        """Get an existing entity by it's business number."""
        try:
            entity = EntityService.find_by_business_identifier(business_identifier, allowed_roles=ALL_ALLOWED_ROLES)
            if entity is not None:
                response, status = entity.as_dict(), http_status.HTTP_200_OK
            else:
                response, status = {'message': f'A business for {business_identifier} was not found.'}, \
                    http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.requires_auth
    def patch(business_identifier):
        """Update an existing business by it's business number."""
        request_json = request.get_json()

        valid_format, errors = schema_utils.validate(request_json, 'entity')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        passcode_reset = request_json.get('resetPasscode', False)

        try:
            if passcode_reset:
                entity = EntityService.reset_passcode(business_identifier,
                                                      email_addresses=request_json.get('passcodeResetEmail', None))
            else:
                entity = EntityService.update_entity(business_identifier, request_json)

            if entity is not None:
                response, status = entity.as_dict(), http_status.HTTP_200_OK
            else:
                response, status = {'message': f'A business for {business_identifier} was not found.'}, \
                    http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @_jwt.has_one_of_roles([Role.SYSTEM.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def delete(business_identifier):
        """Delete an existing entity by it's business number."""
        try:
            entity = EntityService.find_by_business_identifier(business_identifier, allowed_roles=ALL_ALLOWED_ROLES)

            if entity:
                entity.delete()
                response, status = {}, http_status.HTTP_204_NO_CONTENT
            else:
                response, status = {'message': f'A business for {business_identifier} was not found.'}, \
                    http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

        return response, status


@cors_preflight('DELETE,POST,PUT,OPTIONS')
@API.route('/<string:business_identifier>/contacts', methods=['DELETE', 'POST', 'PUT', 'OPTIONS'])
class ContactResource(Resource):
    """Resource for managing entity contacts."""

    @staticmethod
    @_jwt.requires_auth
    @cors.crossdomain(origin='*')
    def post(business_identifier):
        """Add a new contact for the Entity identified by the provided id."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            entity = EntityService.find_by_business_identifier(business_identifier, allowed_roles=ALL_ALLOWED_ROLES)
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
    @_jwt.requires_auth
    @cors.crossdomain(origin='*')
    def put(business_identifier):
        """Update the business contact for the Entity identified by the provided id."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            entity = EntityService.find_by_business_identifier(business_identifier, allowed_roles=ALL_ALLOWED_ROLES)
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
    @_jwt.requires_auth
    @cors.crossdomain(origin='*')
    def delete(business_identifier):
        """Delete the business contact for the Entity identified by the provided id."""
        try:
            entity = EntityService.find_by_business_identifier(business_identifier, allowed_roles=CLIENT_AUTH_ROLES)
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
    @_jwt.requires_auth
    @cors.crossdomain(origin='*')
    def get(business_identifier):
        """Return authorization for the user for the passed business identifier."""
        expanded: bool = request.args.get('expanded', False)
        authorisations = AuthorizationService.get_user_authorizations_for_entity(business_identifier, expanded)
        return authorisations, http_status.HTTP_200_OK
