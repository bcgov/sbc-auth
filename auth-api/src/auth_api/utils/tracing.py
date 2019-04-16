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
"""Function to tracing all methods, functions or exceptions."""
import opentracing
from opentracing.ext import tags


class ExceptionTracing(opentracing.Tracer):
    """
    Tracer that can trace certain exceptions.

    @param tracer the OpenTracing tracer implementation to trace exceptions with
    """

    def __init__(self, tracer=None):

        if not callable(tracer):
            self.__tracer = tracer
            self.__tracer_getter = None
        else:
            self.__tracer = None
            self.__tracer_getter = tracer

    @property
    def tracer(self):
        if not self.__tracer:
            if self.__tracer_getter is None:
                return opentracing.tracer

            self.__tracer = self.__tracer_getter()

        return self.__tracer

    def trace(self):
        """
        Function decorator that traces functions

        NOTE: Must be placed after the @app.route decorator

        (strings) to be set as tags on the created span
        """
        def decorator(f):
            def wrapper(*args, **kwargs):
                self._before_exception_fn(*args)
                try:
                    r = f(*args, **kwargs)
                except Exception:
                    raise

                return r

            wrapper.__name__ = f.__name__
            return wrapper
        return decorator

    def _before_exception_fn(self, *args):
        item = args[0]

        operation_name = item.__class__.__name__

        try:
            span_ctx = self.tracer.active_span
            scope = self.tracer.start_active_span(operation_name,
                                                  child_of=span_ctx)
        except (opentracing.InvalidCarrierException,
                opentracing.SpanContextCorruptedException):
            scope = self.tracer.start_active_span(operation_name)

        span = scope.span
        span.set_tag(tags.ERROR, 'true')
        span.log_kv({'event': 'error',
                     'error.kind': tags.SPAN_KIND_RPC_SERVER,
                     'error.message': item.error,
                     'error.object': operation_name})
        scope.close()
