# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Liclearcense is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This model manages a Membership item in the Auth Service.

The Membership object connects Invitation model to Org and Membership models.
"""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class InvitationMembership(BaseModel):  # pylint: disable=too-few-public-methods
    """Model for Invitation Membership.  Associates Invitation, Orgs and Membership type."""

    __tablename__ = 'invitation_memberships'

    id = Column(Integer, primary_key=True)
    invitation_id = Column(ForeignKey('invitations.id'), nullable=False, index=True)
    org_id = Column(ForeignKey('orgs.id'), nullable=False)
    membership_type_code = Column(ForeignKey('membership_types.code'), nullable=False)

    membership_type = relationship('MembershipType', foreign_keys=[membership_type_code])
    org = relationship('Org', foreign_keys=[org_id])
    invitation = relationship('Invitation', foreign_keys=[invitation_id])
