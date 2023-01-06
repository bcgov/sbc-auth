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
"""Enum definitions."""
from .base_enum import BaseEnum


class AuthHeaderType(BaseEnum):
    """Authorization header types."""

    BASIC = 'Basic {}'
    BEARER = 'Bearer {}'


class ContentType(BaseEnum):
    """Http Content Types."""

    JSON = 'application/json'
    FORM_URL_ENCODED = 'application/x-www-form-urlencoded'
    PDF = 'application/pdf'


class NotificationType(BaseEnum):
    """notification types."""

    ROLE_CHANGED = 'ROLE_CHANGED'
    MEMBERSHIP_APPROVED = 'MEMBERSHIP_APPROVED'


class CorpType(BaseEnum):
    """Corp Types."""

    NR = 'NR'
    CP = 'CP'  # cooperative
    TMP = 'TMP'
    RTMP = 'RTMP'
    BC = 'BC'  # bcomp
    CR = 'CR'  # corporation
    UL = 'UL'  # Unlimited Liability
    CC = 'CC'  # Community Contribution


class ProductTypeCode(BaseEnum):
    """Product Type code."""

    INTERNAL = 'INTERNAL'
    PARTNER = 'PARTNER'


class RequiredAction(BaseEnum):
    """Keycloak required actions."""

    VERIFY_EMAIL = 'VERIFY_EMAIL'
    UPDATE_PROFILE = 'UPDATE_PROFILE'
    CONFIGURE_TOTP = 'CONFIGURE_TOTP'
    UPDATE_PASSWORD = 'UPDATE_PASSWORD'


class PaymentMethod(BaseEnum):
    """Payment types."""

    CREDIT_CARD = 'CC'
    BCOL = 'DRAWDOWN'
    DIRECT_PAY = 'DIRECT_PAY'
    ONLINE_BANKING = 'ONLINE_BANKING'
    PAD = 'PAD'
    EJV = 'EJV'


class PaymentAccountStatus(BaseEnum):
    """Payment types."""

    CREATED = 'CREATED'
    PENDING = 'PENDING'
    FAILED = 'FAILED'


class OrgType(BaseEnum):
    """Org types."""

    PREMIUM = 'PREMIUM'
    BASIC = 'BASIC'
    STAFF = 'STAFF'
    SBC_STAFF = 'SBC_STAFF'


class DocumentType(BaseEnum):
    """Document types."""

    TERMS_OF_USE = 'termsofuse'
    TERMS_OF_USE_DIRECTOR_SEARCH = 'termsofuse_directorsearch'
    TERMS_OF_USE_GOVM = 'termsofuse_govm'
    AFFIDAVIT = 'affidavit'
    TERMS_OF_USE_PAD = 'termsofuse_pad'


class NRStatus(BaseEnum):
    """NR statuses."""

    APPROVED = 'APPROVED'
    CONDITIONAL = 'CONDITIONAL'
    DRAFT = 'DRAFT'
    CONSUMED = 'CONSUMED'


class NRNameStatus(BaseEnum):
    """NR name statuses."""

    APPROVED = 'APPROVED'
    CONDITION = 'CONDITION'


class AffidavitStatus(BaseEnum):
    """Affidavit statuses."""

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    INACTIVE = 'INACTIVE'


class AccessType(BaseEnum):
    """Access Types."""

    REGULAR = 'REGULAR'
    REGULAR_BCEID = 'REGULAR_BCEID'
    EXTRA_PROVINCIAL = 'EXTRA_PROVINCIAL'
    ANONYMOUS = 'ANONYMOUS'
    GOVM = 'GOVM'  # for govt ministry
    GOVN = 'GOVN'  # for govt non-ministry


class Status(BaseEnum):
    """User Membership status."""

    ACTIVE = 1
    INACTIVE = 2
    REJECTED = 3
    PENDING_APPROVAL = 4
    PENDING_STAFF_REVIEW = 5


class UserStatus(BaseEnum):
    """User Membership status."""

    ACTIVE = 1
    INACTIVE = 2


class OrgStatus(BaseEnum):
    """User Membership status."""

    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    REJECTED = 'REJECTED'
    PENDING_ACTIVATION = 'PENDING_ACTIVATION'
    NSF_SUSPENDED = 'NSF_SUSPENDED'
    SUSPENDED = 'SUSPENDED'  # this is basically staff suspended for now
    PENDING_INVITE_ACCEPT = 'PENDING_INVITE_ACCEPT'  # staff invited user and waiting for account creation from user.
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW'  # user created , staff need to approve.


class ProductSubscriptionStatus(BaseEnum):
    """Product Subscription status."""

    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    REJECTED = 'REJECTED'
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW'
    NOT_SUBSCRIBED = 'NOT_SUBSCRIBED'
    SUSPENDED = 'SUSPENDED'  # this is basically staff suspended for now


class SuspensionReasonCode(BaseEnum):
    """Suspension Reason Code for suspending an account."""

    OWNER_CHANGE = 'Account Ownership Change'
    DISPUTE = 'Account Ownership Dispute'
    COURT_ORDER = 'Court Order'
    FRAUDULENT = 'Fraudulent Activity'


class InvitationType(BaseEnum):
    """Invitation type."""

    GOVM = 'GOVM'  # Used to indicate an anonymous account invitation
    DIRECTOR_SEARCH = 'DIRECTOR_SEARCH'  # Used to indicate an anonymous account invitation
    STANDARD = 'STANDARD'  # Used to indicate the standard email invite with admin approval


class IdpHint(BaseEnum):
    """IdpHint for user login."""

    BCROS = 'bcros'
    BCEID = 'bceid'


class InvitationStatus(BaseEnum):
    """Invitation statuses."""

    ACCEPTED = 'ACCEPTED'
    PENDING = 'PENDING'


class LoginSource(BaseEnum):
    """Login source values."""

    PASSCODE = 'PASSCODE'
    BCSC = 'BCSC'
    BCEID = 'BCEID'
    STAFF = 'IDIR'
    BCROS = 'BCROS'
    API_GW = 'API_GW'


class ProductCode(BaseEnum):
    """Product code."""

    BUSINESS = 'BUSINESS'
    BUSINESS_SEARCH = 'BUSINESS_SEARCH'
    VS = 'VS'
    BCA = 'BCA'
    PPR = 'PPR'
    DIR_SEARCH = 'DIR_SEARCH'
    NAMES_REQUEST = 'NRO'
    MHR = 'MHR'


class TaskRelationshipType(BaseEnum):
    """Task relationship type."""

    ORG = 'ORG'  # Task related to Org staff review
    AFFIDAVIT = 'AFFIDAVIT'
    PRODUCT = 'PRODUCT'
    USER = 'USER'


class TaskStatus(BaseEnum):
    """Task relationship type."""

    OPEN = 'OPEN'  # Open Task - needs to be taken action
    COMPLETED = 'COMPLETED'  # Task has been acted upon
    HOLD = 'HOLD'
    CLOSED = 'CLOSED'


class TaskRelationshipStatus(BaseEnum):
    """Task Relationship status."""

    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    REJECTED = 'REJECTED'
    PENDING_ACTIVATION = 'PENDING_ACTIVATION'
    NSF_SUSPENDED = 'NSF_SUSPENDED'
    SUSPENDED = 'SUSPENDED'  # this is basically staff suspended for now
    PENDING_INVITE_ACCEPT = 'PENDING_INVITE_ACCEPT'  # staff invited user and waiting for account creation from user.
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW'  # user created , staff need to approve.


class TaskTypePrefix(BaseEnum):
    """Task Type prefix to be appended to type column while saving a task."""

    NEW_ACCOUNT_STAFF_REVIEW = 'New Account'
    GOVM_REVIEW = 'GovM'
    BCEID_ADMIN = 'BCeID Admin'
    GOVN_REVIEW = 'GovN'


class TaskAction(BaseEnum):
    """Task action."""

    AFFIDAVIT_REVIEW = 'AFFIDAVIT_REVIEW'
    ACCOUNT_REVIEW = 'ACCOUNT_REVIEW'
    PRODUCT_REVIEW = 'PRODUCT_REVIEW'


class ActivityAction(BaseEnum):
    """Different actions in an activity."""

    INVITE_TEAM_MEMBER = 'INVITE_TEAM_MEMBER'
    APPROVE_TEAM_MEMBER = 'APPROVE_TEAM_MEMBER'
    REMOVE_TEAM_MEMBER = 'REMOVE_TEAM_MEMBER'
    RESET_2FA = 'RESET_2FA'
    PAYMENT_INFO_CHANGE = 'PAYMENT_INFO_CHANGE'
    CREATE_AFFILIATION = 'CREATE_AFFILIATION'
    REMOVE_AFFILIATION = 'REMOVE_AFFILIATION'
    ACCOUNT_NAME_CHANGE = 'ACCOUNT_NAME_CHANGE'
    ACCOUNT_ADDRESS_CHANGE = 'ACCOUNT_ADDRESS_CHANGE'
    AUTHENTICATION_METHOD_CHANGE = 'AUTHENTICATION_METHOD_CHANGE'
    ACCOUNT_SUSPENSION = 'ACCOUNT_SUSPENSION'
    ADD_PRODUCT_AND_SERVICE = 'ADD_PRODUCT_AND_SERVICE'


class PatchActions(BaseEnum):
    """Patch Actions."""

    UPDATE_STATUS = 'updateStatus'
    UPDATE_ACCESS_TYPE = 'updateAccessType'

    @classmethod
    def from_value(cls, value):
        """Return instance from value of the enum."""
        return PatchActions(value) if value in cls._value2member_map_ else None  # pylint: disable=no-member
