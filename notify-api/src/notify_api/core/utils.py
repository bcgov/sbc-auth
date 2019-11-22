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
"""Application utils. """
import urllib.request


def download_file(url: str) -> bytes:
    """download file from url."""
    file_contents = None
    with urllib.request.urlopen(url) as response:
        file_contents = response.read()

    return file_contents


def to_camel(string: str) -> str:
    """"convert string to camel format."""
    if '_' not in string or string.startswith('_'):
        return string
    return ''.join([
        x.capitalize() if i > 0 else x
        for i, x in enumerate(string.split('_'))
    ])
