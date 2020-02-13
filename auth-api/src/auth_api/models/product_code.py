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
"""This manages a Product Code record.

It defines the available products.
"""

from .base_model import BaseCodeModel


class ProductCode(BaseCodeModel):  # pylint: disable=too-few-public-methods
    """Product code table to store all the products supported by auth system."""

    __tablename__ = 'product_code'

    @classmethod
    def find_by_code(cls, code):
        """Find a Product Role Code instance that matches the code."""
        return cls.query.filter_by(code=code).one_or_none()
