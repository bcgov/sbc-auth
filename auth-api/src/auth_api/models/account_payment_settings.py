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
from sqlalchemy import Column, ForeignKey, Integer, String, and_, func, Boolean
from sqlalchemy.orm import relationship

from auth_api.utils.roles import OrgStatus as OrgStatusEnum

from .base_model import BaseModel
from .org_status import OrgStatus
from .org_type import OrgType
from .payment_type import PaymentType


class AccountPaymentSettings(BaseModel):  # pylint: disable=too-few-public-methods
    """Model for payment settings record."""

    __tablename__ = 'account_payment_settings'

    id = Column(Integer, primary_key=True)
    preferred_payment_code = Column(ForeignKey('payment_type.code'), nullable=False)
    bcol_user_id = Column(String(20))
    bcol_account_id = Column(String(20))
    org_id = Column(ForeignKey('org.id'), nullable=False)

    org = relationship('Org', foreign_keys=[org_id], lazy='select')
    preferred_payment = relationship('PaymentType')


    @classmethod
    def create_from_dict(cls, payment_info: dict):
        """Create a new Payment Info from the provided dictionary."""
        if payment_info:
            payment_settings = AccountPaymentSettings(**payment_info)
            current_app.logger.debug(
                'Creating payment settings from dictionary {}'.format(payment_info)
            )
            payment_settings.preferred_payment = PaymentType.get_default_payment_type()
            payment_settings.save()
            return payment_settings
        return None