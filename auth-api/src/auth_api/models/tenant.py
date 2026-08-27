# Copyright © 2026 Province of British Columbia
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
"""This manages a Tenant record in the Auth service.

A tenant represents a partner (e.g. a ministry or gov department) that owns
one or more products. Each tenant has an admin org whose ADMIN members act as
tenant administrators.
"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class Tenant(BaseModel):
    """This is the model for a Tenant."""

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_key = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Immutable public identifier, lowercase snake (e.g. 'wills', 'min_agri')",
    )
    name = Column(String(250), nullable=False, comment="Display name (e.g. 'Ministry of Agriculture')")
    description = Column(String(1000), nullable=True)
    admin_org_id = Column(
        ForeignKey("orgs.id"),
        nullable=True,
        comment="Auto-provisioned org whose ADMIN members are the tenant administrators",
    )
    status = Column(String(20), nullable=False, default="ACTIVE", comment="ACTIVE or INACTIVE")

    admin_org = relationship("Org", foreign_keys=[admin_org_id], lazy="select")

    @classmethod
    def find_by_tenant_key(cls, tenant_key: str) -> Tenant | None:
        """Return a Tenant by its immutable key."""
        return cls.query.filter_by(tenant_key=tenant_key).one_or_none()
