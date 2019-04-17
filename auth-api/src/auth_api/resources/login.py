import traceback
from flask import jsonify, request
from flask_restplus import Resource, Namespace
from keycloak import KeycloakOpenID
from auth_api.services import User
import opentracing
from flask_opentracing import FlaskTracing
from ..utils.trace_tags import TraceTags as tags
from flask import current_app
import os
from jose import jwt
from auth_api.utils.util import cors_preflight


API = Namespace('login', description='Authenication System - Passcode login')

# Configure client
keycloak_openid = KeycloakOpenID(server_url=os.getenv("KEYCLOAK_BASE_URL") + "/auth/",
                                 realm_name=os.getenv("KEYCLOAK_REALMNAME"),
                                 client_id=os.getenv("JWT_OIDC_AUDIENCE"),
                                 client_secret_key=os.getenv("JWT_OIDC_CLIENT_SECRET"),
                                 verify=True)


tracer = opentracing.tracer
tracing = FlaskTracing(tracer)


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class login(Resource):
    @staticmethod
    @tracing.trace()
    def post():
        current_span = tracer.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            response = keycloak_openid.token(data['username'], data['password'])
            #response = keycloak_openid.refresh_token(response['refresh_token'])
            # Check if user exists in database, add user if not exists.
            # token = jwt.decode()
            # user = User.find_by_jwt_token(token)
            # if not user:
            #     user = User.save_from_jwt_token(token)
            return response, 200
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            tb = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': tb})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500\



