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

from .affiliation import Affiliation
from .contact import Contact
from .contact_link import ContactLink
from .db import db, ma
from .entity import Entity
from .membership import Membership
from .membership_type import MembershipType
from .org import Org
from .org_status import OrgStatus
from .org_type import OrgType
from .payment_type import PaymentType
from .user import User


event.listen(Engine, 'before_cursor_execute', DBTracing.query_tracing)
