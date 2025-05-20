# Copyright © 2025 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Service for managing Affiliation Mapping data."""
import datetime
from sqlalchemy import and_, or_
import re
from dataclasses import asdict
from typing import Dict, List, Optional

from flask import current_app
from requests.exceptions import HTTPError
from sqlalchemy.orm import contains_eager, subqueryload
from structured_logging import StructuredLogging

from auth_api.exceptions.errors import Error
from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.entity import Entity
from auth_api.models.affiliation_mapping import AffiliationMapping
from auth_api.models.dataclass import AffiliationSearchDetails

logger = StructuredLogging.get_logger()


class AffiliationMappingService:  # pylint: disable=too-few-public-methods
    """Manages all aspect of Affiliation Mapping data.

    This manages updating, retrieving Affiliations in Affilaition Mapping data via the AffiliationMapping model.
    """

    def __init__(self, model):
        """Return an AffiliationMapping Service."""
        self._model = model

    def get_filtered_affiliations(org_id: int, search_details: AffiliationSearchDetails) -> List[AffiliationModel]:
        """Get affiliations from DB based on priority mapping logic.
        - If no filters are applied (initial load), show only top 5 pages max.
        - If filters are applied, allow full pagination.
        """
        # Determine pagination settings
        limit = search_details.limit
        page = search_details.page
        MAX_INITIAL_PAGES = 5

        # Check if it's an unfiltered "initial load"
        is_initial_load = not any(
            [search_details.identifier, search_details.status, search_details.name, search_details.type]
        )

        # If initial load, restrict to first 5 pages
        if is_initial_load and page > MAX_INITIAL_PAGES:
            return []

        offset_value = (page - 1) * limit

        query = (
            db.session.query(AffiliationModel)
            .join(
                AffiliationMapping,
                or_(
                    AffiliationMapping.business_identifier_affilation_id == AffiliationModel.id,
                    and_(
                        AffiliationMapping.business_identifier_affilation_id.is_(None),
                        AffiliationMapping.bootstrap_affilation_id == AffiliationModel.id,
                    ),
                    and_(
                        AffiliationMapping.business_identifier_affilation_id.is_(None),
                        AffiliationMapping.bootstrap_affilation_id.is_(None),
                        AffiliationMapping.nr_affiliation_id == AffiliationModel.id,
                    ),
                ),
            )
            .filter(AffiliationModel.org_id == int(org_id or -1))
        )
        query = query.order_by(AffiliationModel.created.desc()).offset(offset_value).limit(limit)
        return query.all()

    @staticmethod
    def from_entity_details(entity_details: dict) -> AffiliationMapping:
        """Create and populate an AffiliationMapping object from entity details."""
        affiliation_mapping = AffiliationMapping()
        affiliation_mapping.nr_identifier = entity_details.get("nrNumber")
        affiliation_mapping.bootstrap_identifier = entity_details.get("bootstrapIdentifier")
        affiliation_mapping.business_identifier = entity_details.get("identifier")

        # 1. NR Affiliation
        if affiliation_mapping.nr_identifier:
            nr_entity = (
                db.session.query(Entity).filter(Entity.business_identifier == affiliation_mapping.nr_identifier).first()
            )
            if nr_entity:
                nr_affiliation = (
                    db.session.query(AffiliationModel).filter(AffiliationModel.entity_id == nr_entity.id).first()
                )
                if nr_affiliation:
                    affiliation_mapping.nr_affiliation_id = nr_affiliation.id

        # 2. Bootstrap Affiliation
        if affiliation_mapping.bootstrap_identifier:
            bootstrap_entity = (
                db.session.query(Entity)
                .filter(Entity.business_identifier == affiliation_mapping.bootstrap_identifier)
                .first()
            )
            if bootstrap_entity:
                bootstrap_affiliation = (
                    db.session.query(AffiliationModel).filter(AffiliationModel.entity_id == bootstrap_entity.id).first()
                )
                if bootstrap_affiliation:
                    affiliation_mapping.bootstrap_affilation_id = bootstrap_affiliation.id

        # 3. Business Identifier Affiliation
        if affiliation_mapping.business_identifier:
            business_entity = (
                db.session.query(Entity)
                .filter(Entity.business_identifier == affiliation_mapping.business_identifier)
                .first()
            )
            if business_entity:
                business_affiliation = (
                    db.session.query(AffiliationModel).filter(AffiliationModel.entity_id == business_entity.id).first()
                )
                if business_affiliation:
                    affiliation_mapping.business_identifier_affilation_id = business_affiliation.id

        db.session.add(affiliation_mapping)
        db.session.commit()

        return affiliation_mapping
