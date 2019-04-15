# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Endpoints to Authenticate user."""
import traceback
from flask import jsonify, g
from flask_restplus import Resource, Namespace, cors

from auth_api import jwt as _jwt
from auth_api.services import User
from auth_api.utils.util import cors_preflight
from auth_api.utils.trace_tags import TraceTags as tags
from flask import request
import requests

import opentracing
from flask_opentracing import FlaskTracing

API = Namespace('authenticate', description='Authenication System - Authenticate')

# get the existing tracer and inject into flask app
tracer = opentracing.tracer
tracing = FlaskTracing(tracer)


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class User(Resource):
    """Retrieve user detail information from token and database """

    @staticmethod
    @cors.crossdomain(origin='*')
    @tracing.trace()
    def post():
        """Return a JSON object that includes user detail information"""
        request_json = request.get_json()
        realm_name = 'fcf0kpqr'
        base_url = 'sso-dev.pathfinder.gov.bc.ca'
        client_id = 'sbc-auth-web'
        client_secret = 'aeb2b9bc-672b-4574-8bc8-e76e853c37cb'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url = 'https://{}/auth/realms/{}/protocol/openid-connect/token'.format(base_url, realm_name)
        body = 'grant_type=password&client_id={}&username={}&password={}&client_secret={}'\
            .format(client_id, request_json.get('corp_num'), request_json.get('passcode'), client_secret)
        response = requests.post(url, data=body, headers=headers)
        print(response)
        return response.textus

