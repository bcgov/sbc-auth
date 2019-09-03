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
from auth_api.schemas import utils as schema_utils
from auth_api.services import Affiliation as AffiliationService
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight


API = Namespace('orgs', description='Endpoints for organization management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class Orgs(Resource):
    """Resource for managing orgs."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def post():
        """Post a new org using the request body.

        If the org already exists, update the attributes.
        """
        token = g.jwt_oidc_token_info
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'org')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            user = UserService.find_by_jwt_token(token)
            if user is None:
                response, status = {'message': 'Not authorized to perform this action'}, \
                    http_status.HTTP_401_UNAUTHORIZED
            else:
                response, status = OrgService.create_org(request_json, user.identifier).as_dict(), \
                    http_status.HTTP_201_CREATED
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('GET,PUT,OPTIONS')
@API.route('/<string:org_id>', methods=['GET', 'PUT'])
class Org(Resource):
    """Resource for managing a single org."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def get(org_id):
        """Get the org specified by the provided id."""
        org = OrgService.find_by_org_id(org_id)
        if org is None:
            response, status = {'message': 'The requested organization could not be found.'}, \
                http_status.HTTP_404_NOT_FOUND
        else:
            response, status = org.as_dict(), http_status.HTTP_200_OK
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def put(org_id):
        """Update the org specified by the provided id with the request body."""
        org = OrgService.find_by_org_id(org_id)
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'org')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            response, status = org.update_org(request_json).as_dict(), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('DELETE,POST,PUT,OPTIONS')
@API.route('/<string:org_id>/contacts', methods=['DELETE', 'POST', 'PUT'])
class OrgContacts(Resource):
    """Resource for managing org contacts."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def post(org_id):
        """Create a new contact for the specified org."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            org = OrgService.find_by_org_id(org_id)
            if org:
                response, status = org.add_contact(request_json).as_dict(), http_status.HTTP_201_CREATED
            else:
                response, status = {'message': 'The requested organization could not be found.'}, \
                    http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def put(org_id):
        """Update an existing contact for the specified org."""
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'contact')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST
        try:
            org = OrgService.find_by_org_id(org_id)
            if org:
                response, status = org.update_contact(request_json).as_dict(), http_status.HTTP_200_OK
            else:
                response, status = {'message': 'The requested organization could not be found.'}, \
                    http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.requires_auth
    def delete(org_id):
        """Delete the contact info for the specified org."""
        try:
            org = OrgService.find_by_org_id(org_id)
            if org:
                response, status = org.delete_contact().as_dict(), http_status.HTTP_200_OK
            else:
                response, status = {'message': 'The requested organization could not be found.'}, \
                    http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @cors_preflight('GET,POST,OPTIONS')
    @API.route('/<string:org_id>/affiliations', methods=['GET', 'POST', 'OPTIONS'])
    class OrgAffiliations(Resource):
        """Resource for managing affiliations for an org."""

        @staticmethod
        @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
        @TRACER.trace()
        @cors.crossdomain(origin='*')
        def post(org_id):
            """Post a new Affiliation for an org using the request body."""
            request_json = request.get_json()
            valid_format, errors = schema_utils.validate(request_json, 'affiliation')
            if not valid_format:
                return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

            try:
                response, status = AffiliationService \
                    .create_affiliation(org_id, request_json.get('businessIdentifier'),
                                        request_json.get('passCode')).as_dict(), http_status.HTTP_201_CREATED

            except BusinessException as exception:
                response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

            return response, status

        @staticmethod
        @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
        @TRACER.trace()
        @cors.crossdomain(origin='*')
        def get(org_id):
            """Get all affiliated entities for the given org."""
            try:
                response, status = jsonify(AffiliationService.find_affiliated_entities_by_org_id(org_id)), \
                    http_status.HTTP_200_OK

            except BusinessException as exception:
                response, status = {'code': exception.code, 'message': exception.message}, exception.status_code

            return response, status

    @cors_preflight('DELETE,OPTIONS')
    @API.route('/<string:org_id>/affiliations/<string:business_identifier>', methods=['DELETE', 'OPTIONS'])
    class OrgAffiliation(Resource):
        """Resource for managing a single affiliation between an org and an entity."""

        @staticmethod
        @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
        @TRACER.trace()
        @cors.crossdomain(origin='*')
        def delete(org_id, business_identifier):
            """Delete an affiliation between an org and an entity."""
            try:
                AffiliationService.delete_affiliation(org_id, business_identifier)
                response, status = {}, http_status.HTTP_200_OK

            except BusinessException as exception:
                response, status = {'code': exception.code, 'message': exception.message}, \
                    exception.status_code

            return response, status
