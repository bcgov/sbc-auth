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

from auth_api import status as http_status


class Error(Enum):
    """Error Codes."""

    INVALID_INPUT = 'Invalid input, please check.', http_status.HTTP_400_BAD_REQUEST
    DATA_NOT_FOUND = 'No matching record found.', http_status.HTTP_404_NOT_FOUND
    DATA_ALREADY_EXISTS = 'The data you want to insert already exists.', http_status.HTTP_400_BAD_REQUEST
    INVALID_USER_CREDENTIALS = 'Invalid user credentials.', http_status.HTTP_401_UNAUTHORIZED
    INVALID_REFRESH_TOKEN = 'Invalid refresh token.', http_status.HTTP_400_BAD_REQUEST
    UNDEFINED_ERROR = 'Undefined error.', http_status.HTTP_400_BAD_REQUEST
    DATA_CONFLICT = 'New data conflict with existing data.', http_status.HTTP_409_CONFLICT
    ACTIONED_INVITATION = 'The invitation has already been accepted.', http_status.HTTP_400_BAD_REQUEST
    EXPIRED_INVITATION = 'The invitation has expired.', http_status.HTTP_400_BAD_REQUEST
    FAILED_INVITATION = 'Failed to dispatch the invitation', http_status.HTTP_500_INTERNAL_SERVER_ERROR
    FAILED_NOTIFICATION = 'Failed to dispatch the notification', http_status.HTTP_500_INTERNAL_SERVER_ERROR
    DELETE_FAILED_ONLY_OWNER = 'Cannot delete as user is the only owner of some teams', http_status.HTTP_400_BAD_REQUEST
    DELETE_FAILED_INACTIVE_USER = 'User is already inactive', http_status.HTTP_400_BAD_REQUEST

    def __new__(cls, message, status_code):
        """Attributes for the enum."""
        obj = object.__new__(cls)
        obj.message = message
        obj.status_code = status_code
        return obj
