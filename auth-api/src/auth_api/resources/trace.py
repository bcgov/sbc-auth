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
"""Endpoints to start tracing."""
from flask_restplus import Resource, Namespace

import opentracing
from flask_opentracing import FlaskTracing
from opentracing.propagation import Format
from jaeger_client import Config

from auth_api.utils.trace_tags import TraceTags as tags

API = Namespace('trace', description='Authentication System - Tracing')


def init_tracer(service):
    """ initialize tracer"""
    config = Config(
        config={  # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
            'reporter_batch_size': 1,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


# this call also sets opentracing.tracer
tracer = init_tracer('auth_api')
tracing = FlaskTracing(tracer)


@API.route('')
class Trace(Resource):
    """Get tracing header"""

    @staticmethod
    @tracing.trace()
    def get():
        """Return a JSON object that includes a tracing header."""
        current_span = tracer.active_span
        try:
            #current_span.set_tag(tags.NR_NUMBER, request.args.get('nr'))

            user = get_or_create_user_by_jwt(g.jwt_oidc_token_info)
            current_span.set_tag(tags.USER, user.username)
            trace_header = {}
            tracer.inject(current_span, Format.HTTP_HEADERS, trace_header)
            return jsonify(trace_header), 200
        except Exception as err:

            current_span.set_tag(tags.ERROR, 'true')
            tb = traceback.format_exc()
            current_span.log_kv({'event': 'error',
                                 'error.kind': str(type(err)),
                                 'error.message': err.with_traceback(None),
                                 'error.object': tb})
            current_span.set_tag(tags.HTTP_STATUS_CODE, 500)
            return {"error": "{}".format(err)}, 500
