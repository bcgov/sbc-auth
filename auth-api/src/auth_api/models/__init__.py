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

"""This exports all of the models and schemas used by the application."""
from sqlalchemy import event  # noqa: I001
from sqlalchemy.engine import Engine  # noqa: I001, I003, I004

# noqa: I004
# noqa: I001, I003, I004
from sbc_common_components.tracing.db_tracing import DBTracing  # noqa: I001, I004

from .account_login_options import AccountLoginOptions
from .account_payment_settings import AccountPaymentSettings
from .affidavit import Affidavit
from .affidavit_status import AffidavitStatus
from .affiliation import Affiliation
from .contact import Contact
from .contact_link import ContactLink
from .corp_type import CorpType
from .db import db, ma
from .documents import Documents
from .entity import Entity
from .invitation import Invitation
from .invitation_membership import InvitationMembership
from .invitation_type import InvitationType
from .invite_status import InvitationStatus
from .membership import Membership
from .membership_status_code import MembershipStatusCode
from .membership_type import MembershipType
from .org import Org
from .org_settings import OrgSettings
from .org_status import OrgStatus
from .org_type import OrgType
from .payment_type import PaymentType
from .permissions import Permissions
from .product_code import ProductCode
from .product_role_code import ProductRoleCode
from .product_subscription import ProductSubscription
from .product_subscription_role import ProductSubscriptionRole
from .product_type_code import ProductTypeCode
from .user import User
from .user_settings import UserSettings
from .user_status_code import UserStatusCode


event.listen(Engine, 'before_cursor_execute', DBTracing.query_tracing)
