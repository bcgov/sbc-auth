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

from .enums import OrgStatus, OrgType, ProductSubscriptionStatus, Status


class Role(Enum):
    """User Role."""

    VIEWER = "view"
    EDITOR = "edit"
    PUBLIC_USER = "public_user"
    ACCOUNT_HOLDER = "account_holder"
    GOV_ACCOUNT_USER = "gov_account_user"
    ANONYMOUS_USER = "anonymous_user"
    ACCOUNT_IDENTITY = "account_identity"
    MANAGE_EFT = "manage_eft"
    CHANGE_ADDRESS = "change_address"

    SYSTEM = "system"
    TESTER = "tester"

    EXTERNAL_STAFF_READONLY = "external_staff_readonly"
    STAFF = "staff"
    STAFF_VIEW_ACCOUNTS = "view_accounts"
    STAFF_MANAGE_ACCOUNTS = "manage_accounts"
    STAFF_SEARCH = "search"
    STAFF_CREATE_ACCOUNTS = "create_accounts"
    STAFF_MANAGE_BUSINESS = "manage_business"
    STAFF_SUSPEND_ACCOUNTS = "suspend_accounts"

    # Used by Business-AR / Contact Centre Staff / Maximus Staff to create affiliations (and bypass passcode check)
    SKIP_AFFILIATION_AUTH = "skip_affiliation_auth"

    STAFF_TASK_SEARCH = "staff_task_search"
    VIEW_TASK_DETAILS = "view_task_details"
    VIEW_ACCOUNT_PENDING_INVITATIONS = "view_account_pending_invitations"
    VIEW_MEMBERS_PENDING_INVITATIONS = "view_members_pending_invitations"
    VIEW_ACTIVITY_LOGS = "view_activity_logs"
    MANAGE_RESET_OTP = "manage_reset_otp"


# Membership types
STAFF = "STAFF"
COORDINATOR = "COORDINATOR"
ADMIN = "ADMIN"
USER = "USER"

VALID_STATUSES = (Status.ACTIVE.value, Status.PENDING_APPROVAL.value, Status.PENDING_STAFF_REVIEW.value)
VALID_ORG_STATUSES = (
    OrgStatus.ACTIVE.value,
    OrgStatus.NSF_SUSPENDED.value,
    OrgStatus.SUSPENDED.value,
    OrgStatus.PENDING_INVITE_ACCEPT.value,
    OrgStatus.PENDING_STAFF_REVIEW.value,
)
VALID_SUBSCRIPTION_STATUSES = (
    ProductSubscriptionStatus.ACTIVE.value,
    ProductSubscriptionStatus.PENDING_STAFF_REVIEW.value,
    ProductSubscriptionStatus.REJECTED.value,
)
INVALID_ORG_CREATE_TYPE_CODES = (
    OrgType.SBC_STAFF.value,
    OrgType.STAFF.value,
    OrgType.MAXIMUS_STAFF.value,
    OrgType.CC_STAFF.value,
)

CLIENT_ADMIN_ROLES = (COORDINATOR, ADMIN)
CLIENT_AUTH_ROLES = (*CLIENT_ADMIN_ROLES, USER)
ALL_ALLOWED_ROLES = (*CLIENT_AUTH_ROLES, STAFF)
ALLOWED_READ_ROLES = (*CLIENT_AUTH_ROLES, STAFF, Role.EXTERNAL_STAFF_READONLY.value)
AFFILIATION_ALLOWED_ROLES = (*CLIENT_AUTH_ROLES, STAFF, Role.EXTERNAL_STAFF_READONLY.value)
EXCLUDED_FIELDS = ("status_code", "type_code")

PREMIUM_ORG_TYPES = (OrgType.PREMIUM.value, OrgType.SBC_STAFF.value, OrgType.STAFF.value)
