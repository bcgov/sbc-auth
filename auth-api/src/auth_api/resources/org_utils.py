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

from dataclasses import dataclass
from http import HTTPStatus
from typing import Self

from auth_api.exceptions import BusinessException
from auth_api.schemas import utils as schema_utils
from auth_api.services import Org as OrgService
from auth_api.services import User as UserService


@dataclass
class Result[T]:
    """Encapsulates success value or error response."""

    value: T | None = None
    error: dict | None = None
    status: HTTPStatus = HTTPStatus.OK

    @property
    def is_success(self) -> bool:
        """Return True if the result is successful."""
        return self.error is None

    @property
    def is_failure(self) -> bool:
        """Return True if the result is a failure."""
        return self.error is not None

    @classmethod
    def success(cls, value: T) -> Self:
        """Create a successful result with the given value."""
        return cls(value=value)

    @classmethod
    def failure(cls, message: str, status: HTTPStatus, **extras) -> Self:
        """Create a failure result with the given error message and status."""
        return cls(error={"message": message, **extras}, status=status)


def validate_and_get_user() -> Result:
    """Validate request and get authenticated user."""
    user = UserService.find_by_jwt_token()
    if not user:
        return Result.failure("Not authorized to perform this action", HTTPStatus.UNAUTHORIZED)
    return Result.success(user)


def validate_schema(data: dict, schema_name: str) -> Result:
    """Validate data against a schema."""
    valid, errors = schema_utils.validate(data, schema_name)
    if not valid:
        return Result.failure(schema_utils.serialize(errors), HTTPStatus.BAD_REQUEST)
    return Result.success(True)


def create_org(org_info: dict, user_id: int) -> Result:
    """Create an organization."""
    try:
        org = OrgService.create_org(org_info, user_id)
        return Result.success(org.as_dict())
    except BusinessException as e:
        return Result.failure(e.message, e.status_code, code=e.code, detail=e.detail)


def add_contact(org_id: int, contact_info: dict) -> Result:
    """Add contact to organization."""
    try:
        contact = OrgService.add_contact(org_id, contact_info)
        return Result.success(contact.as_dict())
    except BusinessException as e:
        return Result.failure(e.message, e.status_code, code=e.code)
