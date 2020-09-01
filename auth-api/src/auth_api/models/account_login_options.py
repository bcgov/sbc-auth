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
"""This manages the login options for an account/org."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import VersionedModel


class AccountLoginOptions(VersionedModel):  # pylint: disable=too-few-public-methods
    """Model for Account login options."""

    __tablename__ = 'account_login_options'

    id = Column(Integer, primary_key=True)
    login_source = Column(String(20), nullable=False)
    org_id = Column(ForeignKey('org.id'), nullable=False)
    is_active = Column(Boolean(), default=True)

    org = relationship('Org', foreign_keys=[org_id], lazy='select')

    @classmethod
    def find_active_by_org_id(cls, account_id):
        """Find an account setting instance that matches the provided org_id."""
        return cls.query.filter_by(org_id=account_id).filter_by(is_active=True).first()
