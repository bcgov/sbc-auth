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


class NotificationType(Enum):
    """notification types."""

    ROLE_CHANGED = 'ROLE_CHANGED'
    MEMBERSHIP_APPROVED = 'MEMBERSHIP_APPROVED'


class CorpType(Enum):
    """Corp Types."""

    NR = 'NR'


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
