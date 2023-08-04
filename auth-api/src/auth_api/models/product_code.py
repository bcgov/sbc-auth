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
    # this mapper is used so that new and old versions of the service can be run simultaneously,
    # making rolling upgrades easier
    # This is used by SQLAlchemy to explicitly define which fields we're interested
    # so it doesn't freak out and say it can't map the structure if other fields are present.
    # This could occur from a failed deploy or during an upgrade.
    # The other option is to tell SQLAlchemy to ignore differences, but that is ambiguous
    # and can interfere with Alembic upgrades.
    #
    # NOTE: please keep mapper names in alpha-order, easier to track that way
    #       Exception, id is always first, _fields first
    __mapper_args__ = {
        'include_properties': [
            'code',
            'default',
            'description',
            'hidden',
            'keycloak_group',
            'linked_product_code',
            'need_review',
            'parent_code',
            'premium_only',
            'type_code',
            'url'
        ]
    }

    type_code = Column(ForeignKey('product_type_codes.code'), default='INTERNAL', nullable=False)
    parent_code = Column(String(75), nullable=True)  # Used for sub products to define a parent product code
    premium_only = Column(Boolean(), default=False, nullable=True)  # Available only for premium accounts
    need_review = Column(Boolean(), default=False, nullable=True)  # Need a review from staff for activating product
    hidden = Column(Boolean(), default=False, nullable=True)  # Flag to hide from the UI
    linked_product_code = Column(String(100),
                                 nullable=True)  # Product linked to to another product, like business and NR
    keycloak_group = Column(String(100), nullable=True)
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
