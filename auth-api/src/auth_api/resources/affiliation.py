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
"""API endpoints for managing an affiliation resource."""

from flask import current_app, g, request
from flask_restplus import Namespace, Resource, cors
from sqlalchemy import exc

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.schemas import utils as schema_utils
from auth_api.services.affiliation import Affiliation as AffiliationService
from flask import jsonify
from auth_api.tracer import Tracer
from auth_api.utils.roles import Role
from auth_api.utils.util import cors_preflight


API = Namespace('affiliations', description='Affiliations')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight(['GET', 'POST', 'OPTIONS'])
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class AffiliationResources(Resource):
    """Resource for managing affiliations."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def post(org_id):
        """Post a new Affiliation using the request body."""
        current_app.logger.info('<Affiliation.post')
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'affiliation')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            response, status = AffiliationService.create_affiliation(org_id, request_json), http_status.HTTP_201_CREATED

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        except exc.IntegrityError as ex:
            current_app.logger.debug(ex)
            response, status = {'message': 'Affiliation with specified identifier already exists.'}, \
                               http_status.HTTP_409_CONFLICT
        current_app.logger.debug('>Affiliation.post')

        return response, status

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(org_id):
        """Get an existing affiliations by it's org_id."""
        current_app.logger.info('<Affiliation.get')
        try:
            response, status = AffiliationService.find_affiliations_by_org_id(org_id), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        current_app.logger.debug('>Affiliation.get')
        return jsonify(response), status


@cors_preflight(['GET', 'PUT', 'OPTIONS'])
@API.route('/<affiliation_id>', methods=['GET', 'PUT', 'OPTIONS'])
class AffiliationResources(Resource):
    """Resource for managing entities."""

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get(org_id, affiliation_id):
        """Get an existing affiliation by it's org_id and affiliation_id."""
        current_app.logger.info('<Affiliation.get by affiliation id')
        try:
            response, status = AffiliationService.find_affiliation_by_ids(org_id, affiliation_id), \
                               http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        current_app.logger.info('>Affiliation.get by affiliation id')
        return jsonify(response), status

    @staticmethod
    @_JWT.has_one_of_roles([Role.BASIC.value, Role.PREMIUM.value])
    @cors.crossdomain(origin='*')
    def put(org_id, affiliation_id):
        """Update the affiliation for the Affiliation id by the provided id."""
        current_app.logger.info('<Affiliation.put for specified org id and affiliation id')
        request_json = request.get_json()
        valid_format, errors = schema_utils.validate(request_json, 'affiliation')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            response, status = AffiliationService.update_affiliation(org_id, affiliation_id, request_json).as_dict(), \
                               http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        current_app.logger.info('>Affiliation.put for specified org id and affiliation id')
        return response, status