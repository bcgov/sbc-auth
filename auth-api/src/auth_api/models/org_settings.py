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
"""This manages an Org Status record in the Auth service.

This is a mapping between status codes and descriptions for Org objects.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import VersionedModel


class OrgSettings(VersionedModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This is the model for an Org Settings record."""

    __tablename__ = 'org_settings'

    id = Column(Integer, primary_key=True)
    org_id = Column(ForeignKey('org.id'), nullable=False)
    setting = Column(String(100))
    enabled = Column(Boolean(), default=False, nullable=False)
    org = relationship('Org')

    @classmethod
    def get_org_settings(cls, org_id):
        """Return the default status code for an Org."""
        return cls.query.filter_by(org_id=org_id).all()

    @classmethod
    def is_admin_auto_approved_invitees(cls, org_id):
        """Return the default status code for an Org."""
        org_model = cls.query.filter_by(org_id=org_id, setting='ADMIN_AUTO_APPROVAL_FOR_MEMBER_ACCEPTANCE').first()
        if org_model is not None:
            return org_model.enabled
        return False
