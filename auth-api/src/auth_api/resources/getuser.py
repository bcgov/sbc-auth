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
from auth_api.utils.util import cors_preflight
from auth_api.utils import util_keycloak


API = Namespace('getuser', description='Authenication System - Get user by username')

tracer = opentracing.tracer
tracing = FlaskTracing(tracer)


@cors_preflight('GET')
@API.route('')
class getuser(Resource):
    @staticmethod
    @tracing.trace()
    def get():
        current_span = tracer.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            user = util_keycloak.get_user_by_username(data["username"])
            return user, 200
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            tb = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': tb})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500\



