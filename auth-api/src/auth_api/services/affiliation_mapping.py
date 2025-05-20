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
                    AffiliationMapping.business_identifier_affiliation_id == AffiliationModel.id,
                    and_(
                        AffiliationMapping.business_identifier_affiliation_id.is_(None),
                        AffiliationMapping.bootstrap_affiliation_id == AffiliationModel.id,
                    ),
                    and_(
                        AffiliationMapping.business_identifier_affiliation_id.is_(None),
                        AffiliationMapping.bootstrap_affiliation_id.is_(None),
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

        def resolve_affiliation_id(identifier: str) -> Optional[int]:
            """Resolves the affiliation ID based on a given business identifier."""
            if not identifier:
                return None

            result = (
                db.session.query(AffiliationModel.id)
                .join(Entity, AffiliationModel.entity_id == Entity.id)
                .filter(Entity.business_identifier == identifier)
                .first()
            )
            return result[0] if result else None

        # Populate affiliation ids
        affiliation_mapping.nr_affiliation_id = resolve_affiliation_id(affiliation_mapping.nr_identifier)
        affiliation_mapping.bootstrap_affiliation_id = resolve_affiliation_id(affiliation_mapping.bootstrap_identifier)
        affiliation_mapping.business_identifier_affiliation_id = resolve_affiliation_id(
            affiliation_mapping.business_identifier
        )

        db.session.add(affiliation_mapping)
        db.session.commit()

        return affiliation_mapping
