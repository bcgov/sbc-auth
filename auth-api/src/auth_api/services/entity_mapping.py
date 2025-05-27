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
from typing import List

from flask import current_app
from requests import HTTPError
from sqlalchemy import and_, or_
from structured_logging import StructuredLogging

from auth_api.exceptions.exceptions import ServiceUnavailableException
from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.dataclass import AffiliationSearchDetails
from auth_api.models.entity import Entity
from auth_api.models.entity_mapping import EntityMapping
from auth_api.services.rest_service import RestService

logger = StructuredLogging.get_logger()


class EntityMappingService:
    """Manages all aspect of Entity Mapping data.

    This manages updating, retrieving Affiliations in Entity Mapping data via the EntityMapping model.
    """

    @staticmethod
    def get_filtered_affiliations(org_id: int, search_details: AffiliationSearchDetails) -> List[AffiliationModel]:
        """Get affiliations from DB based on priority mapping logic.
        - If no filters are applied (initial load), show only 1 page with 100 results.
        - If filters are applied grab all identifiers
        """
        paginate_for_non_search = not any(
            [search_details.identifier, search_details.status, search_details.name, search_details.type]
        )

        query = (
            db.session.query(AffiliationModel)
            .join(Entity, Entity.id == AffiliationModel.entity_id)
            .join(
                EntityMapping,
                or_(
                    EntityMapping.business_identifier == Entity.business_identifier,
                    and_(
                        EntityMapping.business_identifier.is_(None),
                        EntityMapping.bootstrap_identifier == Entity.business_identifier,
                    ),
                    and_(
                        EntityMapping.business_identifier.is_(None),
                        EntityMapping.bootstrap_identifier.is_(None),
                        EntityMapping.nr_identifier == Entity.business_identifier,
                    ),
                ),
            )
            .filter(AffiliationModel.org_id == int(org_id or -1), Entity.is_loaded_lear.is_(True))
        ).order_by(AffiliationModel.created.desc())

        if paginate_for_non_search:
            limit = search_details.limit
            page = search_details.page
            offset_value = (page - 1) * limit
            query = query.offset(offset_value).limit(limit)
        return query.all()

    @staticmethod
    def from_entity_details(entity_details: dict, use_flush: bool = False) -> EntityMapping:
        """Create and populate an EntityMapping object from entity details."""
        nr_identifier = entity_details.get("nrNumber")
        bootstrap_identifier = entity_details.get("bootstrapIdentifier")
        business_identifier = entity_details.get("identifier")

        affiliation_mapping = (
            db.session.query(EntityMapping)
            .filter(
                or_(
                    EntityMapping.nr_identifier == nr_identifier if nr_identifier else False,
                    EntityMapping.bootstrap_identifier == bootstrap_identifier if bootstrap_identifier else False,
                    EntityMapping.business_identifier == business_identifier if business_identifier else False,
                )
            )
            .first()
        ) or EntityMapping()

        affiliation_mapping.nr_identifier = nr_identifier or affiliation_mapping.nr_identifier
        affiliation_mapping.bootstrap_identifier = bootstrap_identifier or affiliation_mapping.bootstrap_identifier
        affiliation_mapping.business_identifier = business_identifier or affiliation_mapping.business_identifier

        if use_flush:
            affiliation_mapping.flush()
        else:
            affiliation_mapping.save()
        return affiliation_mapping

    @staticmethod
    def get_identifiers_without_mappings(org_id: int) -> List[str]:
        """Find all business identifiers for an org that don't have corresponding entity mappings.

        This joins the affiliation and entity tables, then finds records where there is no
        matching entity mapping for any of the identifiers (business, bootstrap, or NR).
        """
        results = (
            db.session.query(Entity.business_identifier)
            .join(AffiliationModel, Entity.id == AffiliationModel.entity_id)
            .outerjoin(
                EntityMapping,
                or_(
                    EntityMapping.business_identifier == Entity.business_identifier,
                    and_(
                        EntityMapping.business_identifier.is_(None),
                        EntityMapping.bootstrap_identifier == Entity.business_identifier,
                    ),
                    and_(
                        EntityMapping.business_identifier.is_(None),
                        EntityMapping.bootstrap_identifier.is_(None),
                        EntityMapping.nr_identifier == Entity.business_identifier,
                    ),
                ),
            )
            .filter(AffiliationModel.org_id == org_id, EntityMapping.id.is_(None), Entity.is_loaded_lear.is_(True))
            .all()
        )
        return [row[0] for row in results]

    @staticmethod
    def fetch_entity_mappings_details(org_id: int):
        """Return affiliation details by calling the source api."""
        if not (identifiers := EntityMappingService.get_identifiers_without_mappings(org_id)):
            return
        token = RestService.get_service_account_token(
            config_id="ENTITY_SVC_CLIENT_ID", config_secret="ENTITY_SVC_CLIENT_SECRET"
        )
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        new_url = f"{current_app.config.get("LEGAL_API_URL") + current_app.config.get('LEGAL_API_VERSION_2')}"
        endpoint = f"{new_url}/search/affiliation_mappings"
        try:
            response = RestService.post(endpoint, headers, data={"identifiers": identifiers})
            return response.json()
        except HTTPError as http_error:
            # If this fails, we should still allow affiliation search to continue.
            logger.error("Failed to get affiliations mappings for org_id: %s", org_id)
            logger.error(http_error)

    @staticmethod
    def populate_entity_mappings(org_id):
        """Populate the entity mappings for an org."""
        if not (mapping_details := EntityMappingService.fetch_entity_mappings_details(org_id)):
            return
        # We could have a thousand rows, rather do this in one commit instead of multiple.
        for details in mapping_details:
            mapping = EntityMappingService.from_entity_details(details, use_flush=True)
        mapping.save()
