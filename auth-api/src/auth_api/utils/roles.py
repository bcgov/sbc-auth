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

from .enums import Status, OrgStatus


class Role(Enum):
    """User Role."""

    STAFF = 'staff'
    VIEWER = 'viewer'
    EDITOR = 'edit'
    SYSTEM = 'system'
    TESTER = 'tester'
    ACCOUNT_HOLDER = 'account_holder'
    STAFF_ADMIN = 'staff_admin'
    PUBLIC_USER = 'public_user'
    BCOL_STAFF_ADMIN = 'bcol_staff_admin'


# Membership types
STAFF = 'STAFF'
COORDINATOR = 'COORDINATOR'
ADMIN = 'ADMIN'
USER = 'USER'
STAFF_ADMIN = 'STAFF_ADMIN'

VALID_STATUSES = (Status.ACTIVE.value, Status.PENDING_APPROVAL.value)
VALID_ORG_STATUSES = (OrgStatus.ACTIVE.value, OrgStatus.PENDING_AFFIDAVIT_REVIEW.value)

CLIENT_ADMIN_ROLES = (COORDINATOR, ADMIN)
CLIENT_AUTH_ROLES = (*CLIENT_ADMIN_ROLES, USER)
ALL_ALLOWED_ROLES = (*CLIENT_AUTH_ROLES, STAFF, STAFF_ADMIN)
