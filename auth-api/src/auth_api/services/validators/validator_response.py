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
"""Common validator response objects."""

from auth_api.exceptions import Error


class ValidatorResponse:  # pylint: disable=too-few-public-methods; convenience class
    """A convenience class for managing errors as code outside of Exceptions."""

    def __init__(self, error: list[Error] = None, info: dict = None):
        """Initialize the error object."""
        self.error = error if error is not None else []
        self.info = info if info is not None else {}
        self.is_valid = True

    def add_error(self, error: Error):
        """Add error to the response object and make it invalid."""
        self.is_valid = False
        self.error.append(error)

    def add_info(self, info_message: dict):
        """Add to the response [success cases]."""
        self.info.update(info_message)
