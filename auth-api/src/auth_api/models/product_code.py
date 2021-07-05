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
from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, String

from .base_model import BaseCodeModel, db


class ProductCode(BaseCodeModel):  # pylint: disable=too-few-public-methods
    """Product code table to store all the products supported by auth system."""

    __tablename__ = 'product_codes'
    type_code = Column(ForeignKey('product_type_codes.code'), default='INTERNAL', nullable=False)
    premium_only = Column(Boolean(), default=False, nullable=True)  # Available only for premium accounts
    need_review = Column(Boolean(), default=False, nullable=True)  # Need a review from staff for activating product
    hidden = Column(Boolean(), default=False, nullable=True)  # Flag to hide from the UI
    linked_product_code = Column(String(100),
                                 nullable=True)  # Product linked to to another product, like business and NR
    url = Column(String(100), nullable=True)

    @classmethod
    def find_by_code(cls, code):
        """Find a Product Role Code instance that matches the code."""
        return cls.query.filter_by(code=code).one_or_none()

    @classmethod
    def get_all_products(cls):
        """Get all of the products codes."""
        linked_code_subquery = db.session.query(ProductCode.linked_product_code) \
            .filter(ProductCode.linked_product_code.isnot(None)) \
            .subquery()

        return cls.query.filter(ProductCode.code.notin_(linked_code_subquery)).order_by(  # pylint: disable=no-member
            ProductCode.type_code.asc(), ProductCode.description.asc()).all()  # pylint: disable=no-member

    @classmethod
    def get_visible_products(cls):  # pylint: disable=no-member
        """Get all of the products with hidden false."""
        return cls.query.filter_by(hidden=False).order_by(
            ProductCode.type_code.asc(), ProductCode.description.asc()  # pylint: disable=no-member
        ).all()

    @classmethod
    def find_by_type_code(cls, type_code: str) -> List[ProductCode]:
        """Find products by the type code."""
        return cls.query.filter(ProductCode.type_code == type_code).all()
