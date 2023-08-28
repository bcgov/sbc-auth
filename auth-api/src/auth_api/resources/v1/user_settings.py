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
"""API endpoints for managing a User resource."""
import json

from flask import Blueprint, g, jsonify
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.schemas import UserSettingsSchema
from auth_api.services.user import User as UserService
from auth_api.services.user_settings import UserSettings as UserSettingsService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum


bp = Blueprint('USER_SETTINGS', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/users/<string:user_id>/settings')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@TRACER.trace()
@cross_origin(origin='*')
@_jwt.requires_auth
def get_user_settings(user_id):
    """Get info related to the user.

    Currently returns the org details associated with the user.But later can be extended to applications etc
    """
    token = g.jwt_oidc_token_info

    # TODO make this check better.may be read from DB or something
    if token.get('sub', None) != user_id:
        return {'message': 'Unauthorized'}, http_status.HTTP_401_UNAUTHORIZED

    try:
        user = UserService.find_by_jwt_token(silent_mode=True)
        user_id = user.identifier if user else None
        all_settings = UserSettingsService.fetch_user_settings(user_id)
        response, status = jsonify(UserSettingsSchema(many=True).dump(all_settings)), http_status.HTTP_200_OK

    except BusinessException:
        response, status = json.dumps([]), http_status.HTTP_200_OK
    return response, status
