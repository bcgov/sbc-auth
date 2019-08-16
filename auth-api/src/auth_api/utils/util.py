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

"""CORS pre-flight decorator.

A simple decorator to add the options method to a Request Class.
"""

import re


def cors_preflight(methods):
    """Render an option method on the class."""
    def wrapper(f):
        def options(self, *args, **kwargs):  # pylint: disable=unused-argument
            return {'Allow': 'GET'}, 200, \
                   {'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': methods,
                    'Access-Control-Allow-Headers': 'Authorization, Content-Type, registries-trace-id'}

        setattr(f, 'options', options)
        return f
    return wrapper


def camelback2snake(camel_dict: dict):
    """Convert the passed dictionary's keys from camelBack case to snake_case."""
    converted_obj = {}
    for key in camel_dict.keys():
        converted_key = re.sub(r'[A-Z]', lambda x: '_' + x.group(0).lower(), key)
        converted_obj[converted_key] = camel_dict[key]
    return converted_obj


def snake2camelback(snake_dict: dict):
    """Convert the passed dictionary's keys from snake_case to camelBack case."""
    converted_obj = {}
    for key in snake_dict.keys():
        converted_key = re.sub(r'_([a-z])', lambda x: x.group(1).upper(), key)
        converted_obj[converted_key] = snake_dict[key]
    return converted_obj
