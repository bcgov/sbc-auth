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
"""This manage a Payment Type mode. in the Auth service.

Payment types are used to store the preferred payment type on the Org model.
"""

from .base_model import BaseCodeModel


class PaymentType(BaseCodeModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This is the model for a Payment Type."""

    __tablename__ = "payment_types"

    @classmethod
    def get_default_payment_type(cls):
        """Return the default payment type for an Org."""
        return cls.query.filter_by(default=True).first()
