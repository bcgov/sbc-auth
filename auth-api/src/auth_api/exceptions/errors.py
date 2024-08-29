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
from http import HTTPStatus


class Error(Enum):
    """Error Codes."""

    INVALID_INPUT = "Invalid input, please check.", HTTPStatus.BAD_REQUEST
    DATA_NOT_FOUND = "No matching record found.", HTTPStatus.NOT_FOUND
    DATA_ALREADY_EXISTS = "The data you want to insert already exists.", HTTPStatus.BAD_REQUEST
    INVALID_USER_CREDENTIALS = "Invalid user credentials.", HTTPStatus.UNAUTHORIZED
    INVALID_REFRESH_TOKEN = "Invalid refresh token.", HTTPStatus.BAD_REQUEST
    UNDEFINED_ERROR = "Undefined error.", HTTPStatus.BAD_REQUEST
    DATA_CONFLICT = "New data conflict with existing data.", HTTPStatus.CONFLICT
    ACTIONED_INVITATION = "The invitation has already been accepted.", HTTPStatus.BAD_REQUEST
    ACTIONED_AFFILIATION_INVITATION = (
        "The affiliation invitation has already been accepted.",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_BUSINESS_EMAIL = "Business contact email not valid.", HTTPStatus.BAD_REQUEST
    EXPIRED_INVITATION = "The invitation has expired.", HTTPStatus.BAD_REQUEST
    EXPIRED_AFFILIATION_INVITATION = "The affiliation invitation has expired.", HTTPStatus.BAD_REQUEST
    INVALID_AFFILIATION_INVITATION_STATE = (
        "The affiliation invitation is in an invalid state for this action.",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_AFFILIATION_INVITATION_TOKEN = (
        "The affiliation invitation token is invalid.",
        HTTPStatus.BAD_REQUEST,
    )
    FAILED_AFFILIATION_INVITATION = (
        "Failed to dispatch the affiliation invitation",
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )
    AFFILIATION_INVITATION_BUSINESS_NOT_FOUND = (
        "The business specified for the affiliation invitation could not be found.",
        HTTPStatus.BAD_REQUEST,
    )
    FAILED_INVITATION = "Failed to dispatch the invitation", HTTPStatus.INTERNAL_SERVER_ERROR
    FAILED_NOTIFICATION = "Failed to dispatch the notification", HTTPStatus.INTERNAL_SERVER_ERROR
    DELETE_FAILED_ONLY_OWNER = (
        "Cannot delete as user is the only Account Administrator of some teams",
        HTTPStatus.BAD_REQUEST,
    )
    DELETE_FAILED_INACTIVE_USER = "User is already inactive", HTTPStatus.BAD_REQUEST
    CHANGE_ROLE_FAILED_ONLY_OWNER = "User is only Account Administrator in org", HTTPStatus.BAD_REQUEST
    OWNER_CANNOT_BE_REMOVED = "Account Administrator cannot be removed by anyone", HTTPStatus.BAD_REQUEST
    MAX_NUMBER_OF_ORGS_LIMIT = "Maximum number of organisations reached", HTTPStatus.BAD_REQUEST
    ALREADY_CLAIMED_PASSCODE = "Passcode you entered has already been claimed", HTTPStatus.NOT_ACCEPTABLE
    ORG_CANNOT_BE_DISSOLVED = "Organization cannot be dissolved", HTTPStatus.NOT_ACCEPTABLE
    FAILED_ADDING_USER_IN_KEYCLOAK = "Error adding user to keycloak", HTTPStatus.INTERNAL_SERVER_ERROR
    ACCCESS_TYPE_MANDATORY = "staff created orgs needs access type", HTTPStatus.BAD_REQUEST
    USER_CANT_CREATE_ANONYMOUS_ORG = "Only staff can create anonymous org", HTTPStatus.UNAUTHORIZED
    USER_CANT_CREATE_GOVM_ORG = "Only staff can create govt  ministy org", HTTPStatus.UNAUTHORIZED

    USER_CANT_CREATE_EXTRA_PROVINCIAL_ORG = (
        "Only out of province users can create extra provincial org",
        HTTPStatus.UNAUTHORIZED,
    )
    USER_CANT_CREATE_REGULAR_ORG = (
        "Only out of province users cannot create regular org",
        HTTPStatus.UNAUTHORIZED,
    )
    USER_ALREADY_EXISTS_IN_KEYCLOAK = "User Already exists in keycloak", HTTPStatus.CONFLICT
    USER_ALREADY_EXISTS = "The username is already taken", HTTPStatus.CONFLICT
    FAILED_ADDING_USER_ERROR = "Adding User Failed", HTTPStatus.INTERNAL_SERVER_ERROR
    BCOL_ACCOUNT_ALREADY_LINKED = (
        "The BC Online account you have requested to link is already taken.",
        HTTPStatus.CONFLICT,
    )
    BCOL_INVALID_USERNAME_PASSWORD = "Invalid User Id or Password", HTTPStatus.BAD_REQUEST

    # NR_EXPIRED = 'The specified name request has expired', HTTPStatus.BAD_REQUEST
    NR_CONSUMED = "The specified name request has already been consumed.", HTTPStatus.BAD_REQUEST
    NR_NOT_APPROVED = "The specified name request has not been approved.", HTTPStatus.BAD_REQUEST
    NR_INVALID_STATUS = "The specified name request cannot be used.", HTTPStatus.BAD_REQUEST
    NR_NOT_FOUND = "The specified name request number could not be found.", HTTPStatus.BAD_REQUEST
    NR_NOT_PAID = "The payment for the specified name request number is not complete.", HTTPStatus.BAD_REQUEST
    NR_INVALID_CONTACT = "Invalid email or phone number.", HTTPStatus.BAD_REQUEST
    NR_INVALID_CORP_TYPE = (
        "The business type associated with this name request is not yet supported.",
        HTTPStatus.BAD_REQUEST,
    )
    NR_INVALID_APPLICANTS = (
        "The specified name request must have at least one applicant. Please contact staff to fix this name request.",
        HTTPStatus.BAD_REQUEST,
    )

    ENTITY_DELETE_FAILED = "Cannot delete entity due to related records.", HTTPStatus.BAD_REQUEST

    ACTIVE_AFFIDAVIT_EXISTS = (
        "Cannot upload new affidavit as a Pending affidavit is present.",
        HTTPStatus.BAD_REQUEST,
    )
    BCEID_USERS_CANT_BE_OWNERS = "BCEID Users cant be owners", HTTPStatus.BAD_REQUEST
    ACCOUNT_CREATION_FAILED_IN_PAY = "Account creation failed in Pay", HTTPStatus.INTERNAL_SERVER_ERROR
    GOVM_ACCOUNT_DATA_MISSING = (
        "GOVM account creation needs payment info , gl code and mailing address",
        HTTPStatus.BAD_REQUEST,
    )
    PRODUCT_SUBSCRIPTION_EXISTS = "Org has subscription to the product exists.", HTTPStatus.CONFLICT
    INVALID_PRODUCT_RESUB_STATE = "Product is not in a valid state for re-submission.", HTTPStatus.BAD_REQUEST
    INVALID_PRODUCT_RESUBMISSION = "Product is not valid for re-submission.", HTTPStatus.BAD_REQUEST

    OUTSTANDING_CREDIT = "Account have credits remaining on account.", HTTPStatus.BAD_REQUEST
    TRANSACTIONS_IN_PROGRESS = "Account have payment transactions in progress.", HTTPStatus.BAD_REQUEST
    NOT_ACTIVE_ACCOUNT = "Account is not active.", HTTPStatus.BAD_REQUEST
    PAY_ACCOUNT_DEACTIVATE_ERROR = (
        "An error occurred while attempting to deactivate your account.Please try again",
        HTTPStatus.BAD_REQUEST,
    )
    PATCH_INVALID_ACTION = "PATCH_INVALID_ACTION", HTTPStatus.BAD_REQUEST
    SERVICE_UNAVAILABLE = "3rd party application unavailable", HTTPStatus.SERVICE_UNAVAILABLE
    NOT_AUTHORIZED_TO_PERFORM_THIS_ACTION = "Not authorized to perform this action", HTTPStatus.FORBIDDEN

    def __new__(cls, message, status_code):
        """Attributes for the enum."""
        obj = object.__new__(cls)
        obj.message = message
        obj.status_code = status_code
        return obj
