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
"""This manages an Org record, where an Org associates a User (via a Role) with one or more Entities.

Basic users will have an internal Org that is not created explicitly, but implicitly upon User account creation.
"""

from flask import current_app
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class Org(BaseModel):  # pylint: disable=too-few-public-methods
    """Model for an Org record."""

    __tablename__ = 'org'

    id = Column(Integer, primary_key=True)
    type_code = Column(ForeignKey('org_type.code'), nullable=False)
    status_code = Column(ForeignKey('org_status.code'), nullable=False)
    name = Column(String(250), index=True)
    preferred_payment_code = Column(ForeignKey('payment_type.code'), nullable=False)

    contacts = relationship('ContactLink', back_populates='org')
    org_type = relationship('OrgType')
    org_status = relationship('OrgStatus')
    preferred_payment = relationship('PaymentType')

    @classmethod
    def create_from_dict(cls, org_info: dict):
        """Create a new Org from the provided dictionary."""
        if org_info:
            org = Org(**org_info)
            current_app.logger.debug(
                'Creating org from dictionary {}'.format(org_info)
            )
            org.save()
            return org
        return None
