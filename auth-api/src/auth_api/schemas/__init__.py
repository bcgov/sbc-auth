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
"""Schema package."""

from .activity_log import ActivityLogSchema
from .affidavit import AffidavitSchema
from .affiliation import AffiliationSchema
from .contact import ContactSchema
from .contact_link import ContactLinkSchema
from .corp_type import CorpTypeSchema
from .documents import DocumentSchema
from .entity import EntitySchema
from .affiliation_invitation import AffiliationInvitationSchema
from .invitation import InvitationSchema
from .invitation_membership import InvitationMembershipSchema
from .membership import MembershipSchema
from .membership_status_code import MembershipStatusCodeSchema
from .membership_types import MembershipTypeSchema
from .org import OrgSchema
from .org_type import OrgTypeSchema
from .product_code import ProductCodeSchema
from .product_subscription import ProductSubscriptionSchema
from .suspension_reason_code import SuspensionReasonCodeSchema
from .task import TaskSchema
from .user import UserSchema
from .user_settings import UserSettingsSchema
