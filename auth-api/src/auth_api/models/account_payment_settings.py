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
"""This manages payment settings for an account/org.

Default details will be for CC payment.
"""

from flask import current_app
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import VersionedModel
from .payment_type import PaymentType


class AccountPaymentSettings(VersionedModel):  # pylint: disable=too-few-public-methods
    """Model for payment settings record."""

    __tablename__ = 'account_payment_settings'

    id = Column(Integer, primary_key=True)
    preferred_payment_code = Column(ForeignKey('payment_type.code'), nullable=False)
    bcol_user_id = Column(String(20))
    bcol_account_id = Column(String(20))
    org_id = Column(ForeignKey('org.id'), nullable=False)
    is_active = Column(Boolean(), default=True)

    org = relationship('Org', foreign_keys=[org_id], lazy='select')
    preferred_payment = relationship('PaymentType')

    @classmethod
    def create_from_dict(cls, payment_info: dict):
        """Create a new Payment Info from the provided dictionary."""
        if payment_info:
            payment_settings = AccountPaymentSettings(**payment_info)
            payment_settings.is_active = True
            current_app.logger.debug(
                'Creating payment settings from dictionary {}'.format(payment_info)
            )
            if not payment_info.get('preferred_payment_code', None):
                payment_settings.preferred_payment = PaymentType.get_default_payment_type()

            return payment_settings
        return None

    @classmethod
    def find_by_id(cls, identifier: int):
        """Find payment settings by identifier."""
        return cls.query.filter_by(id=identifier).one_or_none()

    @classmethod
    def find_by_bcol_account_id(cls, bcol_account_id, org_id=None):
        """Find an account setting instance that matches the provided bcol_account_id."""
        query = cls.query.filter_by(bcol_account_id=bcol_account_id).filter_by(is_active=True)
        if org_id:
            query = query.filter(AccountPaymentSettings.org_id != org_id)
        return query.first()

    @classmethod
    def find_active_by_org_id(cls, account_id):
        """Find an account setting instance that matches the provided org_id."""
        return cls.query.filter_by(org_id=account_id).filter_by(is_active=True).first()
