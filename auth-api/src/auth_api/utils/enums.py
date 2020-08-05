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
from enum import Enum


class AuthHeaderType(Enum):
    """Authorization header types."""

    BASIC = 'Basic {}'
    BEARER = 'Bearer {}'


class ContentType(Enum):
    """Http Content Types."""

    JSON = 'application/json'
    FORM_URL_ENCODED = 'application/x-www-form-urlencoded'
    PDF = 'application/pdf'


class NotificationType(Enum):
    """notification types."""

    ROLE_CHANGED = 'ROLE_CHANGED'
    MEMBERSHIP_APPROVED = 'MEMBERSHIP_APPROVED'


class CorpType(Enum):
    """Corp Types."""

    NR = 'NR'
    CP = 'CP'  # cooperative
    TMP = 'TMP'
    BC = 'BC'  # bcomp
    CR = 'CR'  # corporation


class RequiredAction(Enum):
    """Keycloak required actions."""

    VERIFY_EMAIL = 'VERIFY_EMAIL'
    UPDATE_PROFILE = 'UPDATE_PROFILE'
    CONFIGURE_TOTP = 'CONFIGURE_TOTP'
    UPDATE_PASSWORD = 'UPDATE_PASSWORD'


class PaymentType(Enum):
    """Payment types."""

    CREDIT_CARD = 'CC'
    BCOL = 'DRAWDOWN'
    DIRECT_PAY = 'DIRECT_PAY'


class OrgType(Enum):
    """Org types."""

    PREMIUM = 'PREMIUM'
    BASIC = 'BASIC'


class ChangeType(Enum):
    """Org upgrade or downgrade."""

    UPGRADE = 'UPGRADE'
    DOWNGRADE = 'DOWNGRADE'


class DocumentType(Enum):
    """Document types."""

    TERMS_OF_USE = 'termsofuse'
    TERMS_OF_USE_DIRECTOR_SEARCH = 'termsofuse_directorsearch'
    AFFIDAVIT = 'affidavit'


class NRStatus(Enum):
    """NR statuses."""

    APPROVED = 'APPROVED'
    CONDITIONAL = 'CONDITIONAL'


class NRNameStatus(Enum):
    """NR name statuses."""

    APPROVED = 'APPROVED'
    CONDITION = 'CONDITION'


class AffidavitStatus(Enum):
    """Affidavit statuses."""

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'


class AccessType(Enum):
    """Access Types."""

    REGULAR = 'REGULAR'
    REGULAR_BCEID = 'REGULAR_BCEID'
    EXTRA_PROVINCIAL = 'EXTRA_PROVINCIAL'
    ANONYMOUS = 'ANONYMOUS'


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
    PENDING_AFFIDAVIT_REVIEW = 'PENDING_AFFIDAVIT_REVIEW'
    REJECTED = 'REJECTED'
    PENDING_ACTIVATION = 'PENDING_ACTIVATION'


class InvitationType(Enum):
    """Invitation type."""

    DIRECTOR_SEARCH = 'DIRECTOR_SEARCH'  # Used to indicate an anonymous account invitation
    STANDARD = 'STANDARD'  # Used to indicate the standard email invite with admin approval


class IdpHint(Enum):
    """IdpHint for user login."""

    BCROS = 'bcros'
    BCEID = 'bceid'


class InvitationStatus(Enum):
    """Invitation statuses."""

    ACCEPTED = 'ACCEPTED'
    PENDING = 'PENDING'


class LoginSource(Enum):
    """Login source values."""

    PASSCODE = 'PASSCODE'
    BCSC = 'BCSC'
    BCEID = 'BCEID'
    STAFF = 'IDIR'
    BCROS = 'BCROS'


class ProductCode(Enum):
    """Product code."""

    BUSINESS = 'BUSINESS'
    VS = 'VS'
    BCA = 'BCA'
    PPR = 'PPR'
    DIR_SEARCH = 'DIR_SEARCH'
