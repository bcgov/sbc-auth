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
"""Role definitions."""
from enum import Enum


class Role(Enum):
    """User Role."""

    BASIC = 'basic'
    PREMIUM = 'premium'
    STAFF = 'staff'
    VIEWER = 'viewer'
    EDITOR = 'edit'
    ADMIN = 'admin'
    SYSTEM = 'system'
    POSTMAN = 'postman'


# Membership types
STAFF = 'STAFF'
ADMIN = 'ADMIN'
OWNER = 'OWNER'
MEMBER = 'MEMBER'


class Status(Enum):
    """User Membership status."""

    ACTIVE = 1
    INACTIVE = 2
    REJECTED = 3
    PENDING_APPROVAL = 4


class UserStatus(Enum):
    """User Membership status."""

    ACTIVE = 1
    INACTIVE = 2


class OrgStatus(Enum):
    """User Membership status."""

    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    PENDING = 'PENDING'


VALID_STATUSES = (Status.ACTIVE.value, Status.PENDING_APPROVAL.value)

CLIENT_ADMIN_ROLES = (ADMIN, OWNER)
CLIENT_AUTH_ROLES = (*CLIENT_ADMIN_ROLES, MEMBER)
ALL_ALLOWED_ROLES = (*CLIENT_AUTH_ROLES, STAFF)
