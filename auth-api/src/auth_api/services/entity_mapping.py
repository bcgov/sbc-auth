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

from sqlite3 import IntegrityError
from typing import List
from sqlalchemy import and_, or_
from auth_api.exceptions.exceptions import ServiceUnavailableException
from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.entity_mapping import EntityMapping
from auth_api.models.dataclass import AffiliationSearchDetails
from auth_api.models.entity import Entity
from auth_api.services.rest_service import RestService
from structured_logging import StructuredLogging

logger = StructuredLogging.get_logger()
from flask import current_app


class EntityMappingService:  # pylint: disable=too-few-public-methods
    """Manages all aspect of Entity Mapping data.

    This manages updating, retrieving Affiliations in Entity Mapping data via the EntityMapping model.
    """

    def __init__(self, model):
        """Return an EntityMapping Service."""
        self._model = model

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
            .filter(AffiliationModel.org_id == int(org_id or -1))
        ).order_by(AffiliationModel.created.desc())

        if paginate_for_non_search:
            limit = search_details.limit
            page = search_details.page
            offset_value = (page - 1) * limit
            query = query.offset(offset_value).limit(limit)
        return query.all()

    @staticmethod
    def from_entity_details(entity_details: dict) -> EntityMapping:
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
        )

        if not affiliation_mapping:
            affiliation_mapping = EntityMapping()

        affiliation_mapping.nr_identifier = nr_identifier
        affiliation_mapping.bootstrap_identifier = bootstrap_identifier
        affiliation_mapping.business_identifier = business_identifier

        affiliation_mapping.save()
        return affiliation_mapping

    @staticmethod
    async def get_affiliation_mappings(org_id) -> List:
        """Return affiliation details by calling the source api."""
        token = RestService.get_service_account_token(
            config_id="ENTITY_SVC_CLIENT_ID", config_secret="ENTITY_SVC_CLIENT_SECRET"
        )
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        new_url = current_app.config.get("LEAR_AFFILIATION_DETAILS_URL")
        endpoint = f"{new_url}/{org_id}/affiliation_mappings"

        try:
            response = await RestService.async_get_call(endpoint, headers)
            return response
            
        except ServiceUnavailableException as err:
            logger.debug(err)
            logger.debug("Failed to get affiliations mappings:")
            raise ServiceUnavailableException("Failed to get affiliation details") from err

    @staticmethod
    def from_entity_details_batch(entity_details_list: list) -> list:
        results = []
        filtered_list = [
            ed for ed in entity_details_list if ed.get("nrId") or ed.get("bootstrapId") or ed.get("identifier")
        ]
        for entity_details in filtered_list:

            mapped_entity = {
                "nrNumber": entity_details.get("nrId"),
                "bootstrapIdentifier": entity_details.get("bootstrapId"),
                "identifier": entity_details.get("identifier"),
            }
            mapping = EntityMappingService.from_entity_details(mapped_entity)
            mapping.save()

            try:
                db.session.flush()
                results.append(mapping)
            except IntegrityError as e:
                db.session.rollback()
                print(f"Duplicate detected, skipping row: {mapped_entity}")
                continue

        return results
