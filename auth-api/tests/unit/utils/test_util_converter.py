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

"""Tests to verify the converter utilities.

Test-Suite to ensure that the camelCase/snake_case converters are working as expected.
"""

from auth_api.utils.util import camelback2snake, snake2camelback


def test_camel_back_to_snake_case():
    """Assert that conversion from camelBack case to snake_case is functioning properly."""
    camel_back_dictionary = {
        'firstTestKey': 'foo',
        'secondTestKey': 'bar',
        'thirdTestKey': 'sandwich',
        'testkey': 'icecream'
    }

    snake_case_dictionary = camelback2snake(camel_back_dictionary)

    assert snake_case_dictionary
    assert snake_case_dictionary['first_test_key'] == 'foo'
    assert snake_case_dictionary['second_test_key'] == 'bar'
    assert snake_case_dictionary['third_test_key'] == 'sandwich'
    assert snake_case_dictionary['testkey'] == 'icecream'


def test_snake_case_to_camel_back():
    """Assert that conversion from snake_case to camelBack is functioning properly."""
    snake_case_dictionary = {
        'first_test_key': 'foo',
        'second_test_key': 'bar',
        'third_test_key': 'sandwich',
        'testkey': 'icecream'
    }

    camel_back_dictionary = snake2camelback(snake_case_dictionary)

    assert camel_back_dictionary
    assert camel_back_dictionary['firstTestKey'] == 'foo'
    assert camel_back_dictionary['secondTestKey'] == 'bar'
    assert camel_back_dictionary['thirdTestKey'] == 'sandwich'
    assert camel_back_dictionary['testkey'] == 'icecream'
