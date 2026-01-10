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
"""Shared utility functions for org endpoints."""

from http import HTTPStatus

from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService


def validate_and_get_user():
    """Validate request and get authenticated user."""
    user = UserService.find_by_jwt_token()
    if user is None:
        return None, {"message": "Not authorized to perform this action"}, HTTPStatus.UNAUTHORIZED
    return user, None, None


def validate_org_schema(org_info):
    """Validate organization schema."""
    valid_format, errors = schema_utils.validate(org_info, "org")
    if not valid_format:
        return False, {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    return True, None, None


def validate_contact_schema(contact_info):
    """Validate contact schema."""
    valid_format, errors = schema_utils.validate(contact_info, "contact")
    if not valid_format:
        return False, {"message": schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST
    return True, None, None


def create_org_with_validation(org_info, user_id):
    """Create an organization with validation."""
    try:
        org = OrgService.create_org(org_info, user_id)
        return org.as_dict(), None, None
    except BusinessException as exception:
        return (
            None,
            {
                "code": exception.code,
                "message": exception.message,
                "detail": exception.detail,
            },
            exception.status_code,
        )


def add_contact_with_validation(org_id, contact_info):
    """Add contact to organization with validation."""
    try:
        contact = OrgService.add_contact(org_id, contact_info)
        return contact.as_dict(), None, None
    except BusinessException as exception:
        return None, {"code": exception.code, "message": exception.message}, exception.status_code
