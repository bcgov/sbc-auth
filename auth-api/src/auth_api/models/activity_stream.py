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
"""Model for all activity stream related changes.

"""
from flask import current_app
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, and_, func
from sqlalchemy.orm import contains_eager, relationship

from auth_api.utils.enums import AccessType, InvitationStatus, InvitationType, OrgStatus as OrgStatusEnum
from auth_api.utils.roles import VALID_STATUSES, EXCLUDED_FIELDS

from .base_model import VersionedModel, BaseModel
from .contact import Contact
from .contact_link import ContactLink
from .db import db
from .invitation import InvitationMembership
from .invitation import Invitation
from .org_status import OrgStatus
from .org_type import OrgType


class ActivityStream(BaseModel):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Model for ActivityStream Org record."""

    __tablename__ = 'activity_streams'

    id = Column(Integer, primary_key=True)
    actor = Column(String(250))
    action = Column(String(250), index=True)
    item_type = Column(String(250), index=True)
    item_id = Column(Integer)
    remote_addr = Column(String(250), index=False)

