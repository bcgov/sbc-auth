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

from sbc_common_components.tracing.db_tracing import DBTracing
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .affiliation import Affiliation, AffiliationSchema
from .db import db, ma
from .contact import Contact, ContactSchema
from .entity import Entity, EntitySchema
from .membership import Membership, MembershipSchema
from .membership_type import MembershipType, MembershipTypeSchema
from .org import Org, OrgSchema
from .org_status import OrgStatus, OrgStatusSchema
from .org_type import OrgType, OrgTypeSchema
from .payment_type import PaymentType, PaymentTypeSchema
from .user import User, UserSchema


event.listen(Engine, 'before_cursor_execute', DBTracing.query_tracing)
