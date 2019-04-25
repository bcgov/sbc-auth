import traceback
from flask import request
from flask_restplus import Resource, Namespace
from auth_api.services.keycloak import KeycloakService
import opentracing
from flask_opentracing import FlaskTracing
from ..utils.trace_tags import TraceTags as tags
from auth_api.utils.util import cors_preflight


API = Namespace('user', description='Keycloak Admin - user')
KEYCLOAK_SERVICE = KeycloakService()

tracer = opentracing.tracer
tracing = FlaskTracing(tracer)


@cors_preflight('GET, POST, DELETE, OPTIONS')
@API.route('', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])

class user(Resource):
    @staticmethod
    @tracing.trace()
    def post():
        current_span = tracer.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            response = KEYCLOAK_SERVICE.add_user(data)

            return response, 201
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            tb = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': tb})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500\



    @staticmethod
    @tracing.trace()
    def get():
        current_span = tracer.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            user = KEYCLOAK_SERVICE.get_user_by_username(data.get("username"))
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


    @staticmethod
    @tracing.trace()
    def delete():
        current_span = tracer.active_span
        data = request.get_json()
        if not data:
            data = request.values
        try:
            response = KEYCLOAK_SERVICE.delete_user_by_username(data.get("username"))
            return response, 204
        except Exception as err:
            current_span.set_tag(tags.ERROR, 'true')
            tb = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': tb})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500\

