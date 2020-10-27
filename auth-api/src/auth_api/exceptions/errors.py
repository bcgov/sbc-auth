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
    DELETE_FAILED_ONLY_OWNER = 'Cannot delete as user is the only Account Administrator of some teams', \
                               http_status.HTTP_400_BAD_REQUEST
    DELETE_FAILED_INACTIVE_USER = 'User is already inactive', http_status.HTTP_400_BAD_REQUEST
    CHANGE_ROLE_FAILED_ONLY_OWNER = 'User is only Account Administrator in org', http_status.HTTP_400_BAD_REQUEST
    OWNER_CANNOT_BE_REMOVED = 'Account Administrator cannot be removed by anyone', http_status.HTTP_400_BAD_REQUEST
    MAX_NUMBER_OF_ORGS_LIMIT = 'Maximum number of organisations reached', http_status.HTTP_400_BAD_REQUEST
    ALREADY_CLAIMED_PASSCODE = 'Passcode you entered has already been claimed', http_status.HTTP_406_NOT_ACCEPTABLE
    ORG_CANNOT_BE_DISSOLVED = 'Organization cannot be dissolved', http_status.HTTP_406_NOT_ACCEPTABLE
    FAILED_ADDING_USER_IN_KEYCLOAK = 'Error adding user to keycloak', http_status.HTTP_500_INTERNAL_SERVER_ERROR
    USER_CANT_CREATE_ANONYMOUS_ORG = 'Only staff can create anonymous org', http_status.HTTP_401_UNAUTHORIZED
    USER_CANT_CREATE_EXTRA_PROVINCIAL_ORG = 'Only out of province users can create extra provincial org', \
                                            http_status.HTTP_401_UNAUTHORIZED
    USER_CANT_CREATE_REGULAR_ORG = 'Only out of province users cannot create regular org', \
                                   http_status.HTTP_401_UNAUTHORIZED
    USER_ALREADY_EXISTS_IN_KEYCLOAK = 'User Already exists in keycloak', http_status.HTTP_409_CONFLICT
    USER_ALREADY_EXISTS = 'The username is already taken', http_status.HTTP_409_CONFLICT
    FAILED_ADDING_USER_ERROR = 'Adding User Failed', http_status.HTTP_500_INTERNAL_SERVER_ERROR
    BCOL_ACCOUNT_ALREADY_LINKED = 'The BC Online account you have requested to link is already taken.', \
                                  http_status.HTTP_409_CONFLICT
    BCOL_INVALID_USERNAME_PASSWORD = 'Invalid User Id or Password', http_status.HTTP_400_BAD_REQUEST

    # NR_EXPIRED = 'The specified name request has expired', http_status.HTTP_400_BAD_REQUEST
    NR_CONSUMED = 'The specified name request has already been consumed.', http_status.HTTP_400_BAD_REQUEST
    NR_NOT_APPROVED = 'The specified name request has not been approved.', http_status.HTTP_400_BAD_REQUEST
    NR_NOT_FOUND = 'The specified name request number could not be found.', http_status.HTTP_400_BAD_REQUEST
    NR_INVALID_CONTACT = 'Invalid email or phone number.', http_status.HTTP_400_BAD_REQUEST
    NR_INVALID_CORP_TYPE = 'The business type associated with this name request is not yet supported.', \
                           http_status.HTTP_400_BAD_REQUEST

    ENTITY_DELETE_FAILED = 'Cannot delete entity due to related records.', http_status.HTTP_400_BAD_REQUEST

    ACTIVE_AFFIDAVIT_EXISTS = 'Cannot upload new affidavit as a Pending affidavit is present.', \
                              http_status.HTTP_400_BAD_REQUEST
    BCEID_USERS_CANT_BE_OWNERS = 'BCEID Users cant be owners', http_status.HTTP_400_BAD_REQUEST
    ACCOUNT_CREATION_FAILED_IN_PAY = 'Account creation failed in Pay', http_status.HTTP_500_INTERNAL_SERVER_ERROR

    def __new__(cls, message, status_code):
        """Attributes for the enum."""
        obj = object.__new__(cls)
        obj.message = message
        obj.status_code = status_code
        return obj
