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
"""This manages a Product Role Code record.

It defines the available roles for a product.
"""

from sqlalchemy import Column, ForeignKey, Integer, String

from .base_model import BaseModel


class ProductRoleCode(BaseModel):  # pylint: disable=too-few-public-methods
    """Product role code table to store all the roles on products supported by auth system."""

    __tablename__ = 'product_role_code'
    id = Column(Integer, primary_key=True)
    code = Column(String(15), index=True)
    desc = Column(String(100))

    product_code = Column(ForeignKey('product_code.code'), nullable=False)

    @classmethod
    def find_by_code_and_product_code(cls, code: str, product_code: str):
        """Find a Product Role Code instance that matches the code and product code."""
        return cls.query.filter_by(code=code, product_code=product_code).one_or_none()
