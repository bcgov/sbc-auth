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

from flask import Blueprint, request
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services.authorization import Authorization as AuthorizationService
from auth_api.services.contact import Contact as ContactService
from auth_api.services.entity import Entity as EntityService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.roles import ALL_ALLOWED_ROLES, CLIENT_AUTH_ROLES, Role
from auth_api.utils.util import cors_preflight


bp = Blueprint('ENTITIES', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/entities')
TRACER = Tracer.get_instance()


@bp.route('', methods=['POST', 'OPTIONS'])
@_jwt.has_one_of_roles([Role.SYSTEM.value])
@TRACER.trace()
@cross_origin(origin='*')
def post_entity():
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
        entity = EntityService.save_entity(request_json)
        response, status = entity.as_dict(), http_status.HTTP_201_CREATED
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status


@bp.route('/<string:business_identifier>', methods=['GET', 'OPTIONS'])
@_jwt.requires_auth
@TRACER.trace()
@cross_origin(origin='*')
def get_entity(business_identifier):
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


@bp.route('/<string:business_identifier>', methods=['PATCH'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def patch_entity(business_identifier):
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


@bp.route('/<string:business_identifier>', methods=['DELETE'])
@_jwt.has_one_of_roles([Role.SYSTEM.value])
@TRACER.trace()
@cross_origin(origin='*')
def delete_entity(business_identifier):
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


@bp.route('/<string:business_identifier>/contacts', methods=['GET', 'OPTIONS'])
@_jwt.requires_auth
@TRACER.trace()
@cross_origin(origin='*')
def get_entity_contact(business_identifier):
    """Get contact email for the Entity identified by the provided business identifier."""
    # This route allows public users to look at masked email addresses.
    # It's used by the business dashboard for magic link.
    if ((entity := EntityService.find_by_business_identifier(business_identifier, skip_auth=True)) and
            (contact := entity.get_contact())):
        return ContactService(contact).as_dict(masked_email_only=True), http_status.HTTP_200_OK
    return {'message': f'Contacts for {business_identifier} was not found.'}, \
        http_status.HTTP_404_NOT_FOUND


@bp.route('/<string:business_identifier>/contacts', methods=['POST'])
@_jwt.requires_auth
@cross_origin(origin='*')
def post_entity_contact(business_identifier):
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


@bp.route('/<string:business_identifier>/contacts', methods=['PUT'])
@_jwt.requires_auth
@cross_origin(origin='*')
def put_entity_contact(business_identifier):
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


@bp.route('/<string:business_identifier>/contacts', methods=['DELETE'])
@_jwt.requires_auth
@cross_origin(origin='*')
def delete_entity_contact(business_identifier):
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


@bp.route('/<string:business_identifier>/authorizations', methods=['GET', 'OPTIONS'])
@_jwt.requires_auth
@cross_origin(origin='*')
def get_entity_authorizations(business_identifier):
    """Return authorization for the user for the passed business identifier."""
    expanded: bool = request.args.get('expanded', False)
    authorisations = AuthorizationService.get_user_authorizations_for_entity(business_identifier, expanded)
    return authorisations, http_status.HTTP_200_OK
