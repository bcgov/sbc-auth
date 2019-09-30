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
"""Descriptive error codes and descriptions for readability.

Standardize error message to display user friendly messages.
"""

from enum import Enum

from notify_api import status as http_status


class Error(Enum):
    """Error Codes."""

    SEND_EMAIL_FAIL = 'Sending Email failed, please check.', http_status.HTTP_500_INTERNAL_SERVER_ERROR

    def __new__(cls, message, status_code):
        """Attributes for the enum."""
        obj = object.__new__(cls)
        obj.message = message
        obj.status_code = status_code
        return obj
