import traceback
from flask import jsonify, request
from flask_restplus import Resource, Namespace
from keycloak import KeycloakOpenID

import opentracing
from flask_opentracing import FlaskTracing
from ..utils.trace_tags import TraceTags as tags

API = Namespace('login', description='Authenication System - Passcode login')

# Configure client
keycloak_openid = KeycloakOpenID(server_url="https://sso-dev.pathfinder.gov.bc.ca/auth/",
                                 realm_name="fcf0kpqr",
                                 client_id="sbc-auth-cron-job",
                                 client_secret_key="fb1d2705-8323-467b-b67d-467d0a9a0986",
                                 verify=True)

# keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/auth/",
#                                  realm_name="registries",
#                                  client_id="localtest",
#                                  client_secret_key="27f45971-0bee-44da-b5d6-34452a97b0b4",
#                                  verify=True)

tracer = opentracing.tracer
tracing = FlaskTracing(tracer)


@API.route('')
class login(Resource):
    @staticmethod
    @tracing.trace()
    def get():
        current_span = tracer.active_span
        data = request.get_json()
        if (data==None):
            data=request.values
        try:
            token = keycloak_openid.token(data['username'], data['password'])
            token = keycloak_openid.refresh_token(token['refresh_token'])
            return token, 200
        except Exception as err:\
                current_span.set_tag(tags.ERROR, 'true')
        tb = traceback.format_exc()
        current_span.log_kv({'event': 'error',
                             'error.kind': str(type(err)),
                             'error.message': err.with_traceback(None),
                             'error.object': tb})
        current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
        return {"error": "{}".format(err)}, 500\

# @api.route("/logout")
# class logout(Resource):
#     @staticmethod
#     def get():
#         return 200

