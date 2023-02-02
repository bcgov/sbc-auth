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
"""Tracing subsystem class.

This module initializes and provides the tracing component from sbc_common_components
"""

from sbc_common_components.tracing.api_tracer import ApiTracer
from sbc_common_components.tracing.api_tracing import ApiTracing


class Tracer():  # pylint: disable=too-few-public-methods
    """Singleton class that wraps sbc_common_components tracing."""

    __instance = None

    @staticmethod
    def get_instance():
        """Retrieve singleton JWTWrapper."""
        if Tracer.__instance is None:
            Tracer()
        return Tracer.__instance

    def __init__(self):
        """Virtually private constructor."""
        if Tracer.__instance is not None:
            raise Exception('Attempt made to create multiple tracing instances')  # pylint: disable=line-too-long, broad-exception-raised

        api_tracer = ApiTracer()
        Tracer.__instance = ApiTracing(api_tracer.tracer)   # pylint: disable=unused-private-member
