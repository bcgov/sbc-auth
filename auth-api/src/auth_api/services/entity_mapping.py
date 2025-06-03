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
from flask import current_app
from requests import HTTPError
from sqlalchemy import and_, case, func, or_, text
from sqlalchemy.dialects.postgresql import array
from structured_logging import StructuredLogging

from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.dataclass import AffiliationBase, AffiliationSearchDetails
from auth_api.models.entity import Entity
from auth_api.models.entity_mapping import EntityMapping
from auth_api.services.rest_service import RestService
from auth_api.utils.user_context import UserContext, user_context

logger = StructuredLogging.get_logger()


class EntityMappingService:
    """Manages all aspect of Entity Mapping data.

    This manages updating, retrieving Affiliations in Entity Mapping data via the EntityMapping model.
    """

    @staticmethod
    def paginate_from_affiliations(org_id: int, search_details: AffiliationSearchDetails):
        """Get affiliations from DB based on priority mapping logic.
        - If no filters are applied (initial load), show only 1 page with 100 results.
        - If filters are applied grab all identifiers
        - For TEMP business with NR, group them together and count as one row for pagination
        - Returns an array of identifiers where NR+TMP pairs will have both identifiers in the array
        """
        paginate_for_non_search = not any(
            [search_details.identifier, search_details.status, search_details.name, search_details.type]
        )

        # Hide TMP and NR rows when a full business row exists with the same NR
        full_business_nrs = (
            db.session.query(EntityMapping.nr_identifier)
            .select_from(EntityMapping)
            .join(Entity, Entity.business_identifier == EntityMapping.business_identifier)
            .join(AffiliationModel, AffiliationModel.entity_id == Entity.id)
            .filter(
                and_(
                    EntityMapping.nr_identifier.isnot(None),
                    EntityMapping.bootstrap_identifier.isnot(None),
                    EntityMapping.business_identifier.isnot(None),
                    AffiliationModel.org_id == int(org_id or -1),
                    Entity.is_loaded_lear.is_(True),
                )
            )
            .scalar_subquery()
        )

        bootstrap_dates = (
            db.session.query(
                EntityMapping.bootstrap_identifier,
                EntityMapping.nr_identifier,
                AffiliationModel.created.label("bootstrap_created"),
            )
            .join(Entity, Entity.business_identifier == EntityMapping.bootstrap_identifier)
            .join(AffiliationModel, AffiliationModel.entity_id == Entity.id)
            .filter(
                EntityMapping.business_identifier.is_(None),
                EntityMapping.bootstrap_identifier.isnot(None),
                EntityMapping.nr_identifier.isnot(None),
                EntityMapping.nr_identifier.notin_(full_business_nrs),
                AffiliationModel.org_id == int(org_id or -1),
                Entity.is_loaded_lear.is_(True),
            )
            .subquery()
        )

        identifiers_case = case(
            (EntityMapping.business_identifier.isnot(None), array([EntityMapping.business_identifier])),
            (
                and_(EntityMapping.bootstrap_identifier.isnot(None), EntityMapping.nr_identifier.isnot(None)),
                array([EntityMapping.bootstrap_identifier, EntityMapping.nr_identifier]),
            ),
            (EntityMapping.nr_identifier.isnot(None), array([EntityMapping.nr_identifier])),
            (EntityMapping.bootstrap_identifier.isnot(None), array([EntityMapping.bootstrap_identifier])),
        )

        base_query = (
            db.session.query(
                identifiers_case.label("identifiers"),
                func.coalesce(bootstrap_dates.c.bootstrap_created, AffiliationModel.created).label("order_date"),
            )
            .join(Entity, Entity.id == AffiliationModel.entity_id)
            .join(
                EntityMapping,
                or_(
                    # Fully formed business (standalone)
                    EntityMapping.business_identifier == Entity.business_identifier,
                    # TEMP business only, numbered temp filing (standalone)
                    and_(
                        EntityMapping.business_identifier.is_(None),
                        EntityMapping.bootstrap_identifier == Entity.business_identifier,
                        EntityMapping.nr_identifier.is_(None),
                    ),
                    # NR only (standalone)
                    and_(
                        EntityMapping.business_identifier.is_(None),
                        EntityMapping.bootstrap_identifier.is_(None),
                        EntityMapping.nr_identifier == Entity.business_identifier,
                    ),
                    # Named TEMP business with NR (combined info, need both affiliation rows to count as 1)
                    and_(
                        EntityMapping.business_identifier.is_(None),
                        EntityMapping.bootstrap_identifier == Entity.business_identifier,
                        EntityMapping.nr_identifier.isnot(None),
                        EntityMapping.nr_identifier.notin_(full_business_nrs),
                    ),
                ),
            )
            .outerjoin(
                bootstrap_dates,
                and_(
                    EntityMapping.bootstrap_identifier == bootstrap_dates.c.bootstrap_identifier,
                    EntityMapping.nr_identifier == bootstrap_dates.c.nr_identifier,
                ),
            )
            .filter(AffiliationModel.org_id == int(org_id or -1), Entity.is_loaded_lear.is_(True))
            .order_by(text("order_date DESC"))
        )

        if paginate_for_non_search:
            limit = search_details.limit
            page = search_details.page
            offset_value = (page - 1) * limit
            query = base_query.offset(offset_value).limit(limit)
        else:
            query = base_query

        return query.all()

    @staticmethod
    def populate_affiliation_base(org_id: int, search_details: AffiliationSearchDetails):
        """Get entity details from the database and expand multiple identifiers into separate rows."""
        data = EntityMappingService.paginate_from_affiliations(org_id, search_details)
        return [
            AffiliationBase(identifier=identifier, created=created)
            for identifiers, created in data
            for identifier in identifiers
        ]

    @staticmethod
    def _is_duplicate_mapping(nr_identifier: str, bootstrap_identifier: str, business_identifier: str) -> bool:
        """Check if the new mapping data exactly matches an existing mapping."""
        conditions = []
        if nr_identifier:
            conditions.append(EntityMapping.nr_identifier == nr_identifier)
        if bootstrap_identifier:
            conditions.append(EntityMapping.bootstrap_identifier == bootstrap_identifier)
        if business_identifier:
            conditions.append(EntityMapping.business_identifier == business_identifier)
        duplicate = db.session.query(EntityMapping).filter(and_(*conditions)).first()
        return duplicate is not None

    @staticmethod
    def _update_existing_mapping(
        existing_mapping: EntityMapping | None, nr_identifier: str, bootstrap_identifier: str, business_identifier: str
    ) -> bool:
        """Update an existing mapping with new identifiers if they fill in missing values.

        Returns True if the mapping was updated, False otherwise.
        """
        if existing_mapping is None:
            return False
        should_update = False
        if nr_identifier and not existing_mapping.nr_identifier:
            existing_mapping.nr_identifier = nr_identifier
            should_update = True
        if bootstrap_identifier and not existing_mapping.bootstrap_identifier:
            existing_mapping.bootstrap_identifier = bootstrap_identifier
            should_update = True
        if business_identifier and not existing_mapping.business_identifier:
            existing_mapping.business_identifier = business_identifier
            should_update = True

        if should_update:
            logger.debug(
                f"Updating entity mapping {existing_mapping.id} with: "
                f"business_identifier: {business_identifier}, "
                f"bootstrap_identifier: {bootstrap_identifier}, "
                f"nr_identifier: {nr_identifier}"
            )
            existing_mapping.save()
        return should_update

    @staticmethod
    def _build_mapping_conditions(nr_identifier: str, bootstrap_identifier: str, business_identifier: str) -> list:
        """Build conditions for finding an existing mapping based on provided identifiers.

        Each case ensures that other identifiers are None to prevent partial matches.
        """
        # Full business
        if all([nr_identifier, bootstrap_identifier, business_identifier]):
            return [
                EntityMapping.nr_identifier == nr_identifier,
                EntityMapping.bootstrap_identifier == bootstrap_identifier,
                EntityMapping.business_identifier.is_(None),
            ]
        # Numbered business or bootstrap only numbered business
        elif all([bootstrap_identifier, business_identifier]) or (
            bootstrap_identifier and not nr_identifier and not business_identifier
        ):
            return [
                EntityMapping.nr_identifier.is_(None),
                EntityMapping.bootstrap_identifier == bootstrap_identifier,
                EntityMapping.business_identifier.is_(None),
            ]
        # NR and Bootstrap or just NR
        elif all([nr_identifier, bootstrap_identifier]) or (
            nr_identifier and not bootstrap_identifier and not business_identifier
        ):
            return [
                EntityMapping.nr_identifier == nr_identifier,
                EntityMapping.business_identifier.is_(None),
                EntityMapping.bootstrap_identifier.is_(None),
            ]
        # Business only, could be from COLIN
        elif business_identifier and (not nr_identifier and not bootstrap_identifier):
            return [
                EntityMapping.nr_identifier.is_(None),
                EntityMapping.bootstrap_identifier.is_(None),
                EntityMapping.business_identifier == business_identifier,
            ]
        else:
            # Handle not possible cases like NR, no TEMP and BUSINESS IDENTIFIER
            # Log warning instead of raising an exception incase we have some of these weird cases.
            logger.warning(
                f"Invalid identifier combination provided: {nr_identifier},{bootstrap_identifier},{business_identifier}"
            )
            return [
                EntityMapping.id == -1,
            ]

    @staticmethod
    @user_context
    def from_entity_details(entity_details: dict, skip_auth: bool = False, **kwargs):
        """Create and populate an EntityMapping object from entity details.

        Only updates an existing row if the new data fills in missing identifiers.
        Otherwise creates a new row.
        """
        user_from_context: UserContext = kwargs["user_context"]
        if skip_auth is False and not user_from_context.is_system():
            return

        nr_identifier = entity_details.get("nrNumber")
        bootstrap_identifier = entity_details.get("bootstrapIdentifier")
        business_identifier = entity_details.get("identifier")

        if EntityMappingService._is_duplicate_mapping(nr_identifier, bootstrap_identifier, business_identifier):
            return

        conditions = EntityMappingService._build_mapping_conditions(
            nr_identifier, bootstrap_identifier, business_identifier
        )

        existing_mapping = db.session.query(EntityMapping).filter(and_(*conditions)).first()
        if EntityMappingService._update_existing_mapping(
            existing_mapping, nr_identifier, bootstrap_identifier, business_identifier
        ):
            return

        new_mapping = EntityMapping(
            nr_identifier=nr_identifier,
            bootstrap_identifier=bootstrap_identifier,
            business_identifier=business_identifier,
        )
        logger.debug(
            f"Creating new entity mapping with: "
            f"business_identifier: {business_identifier}, "
            f"bootstrap_identifier: {bootstrap_identifier}, "
            f"nr_identifier: {nr_identifier}"
        )
        new_mapping.save()

    @staticmethod
    def populate_entity_mapping_for_identifier(identifier: str):
        """Populate the entity mapping for the identifier."""
        if entity_mapping := EntityMappingService.fetch_entity_mapping_details(identifier):
            EntityMappingService.from_entity_details(entity_mapping[0], skip_auth=True)

    @staticmethod
    def fetch_entity_mapping_details(identifier: str):
        """Return affiliation details by calling the source api."""
        logger.info(f"Fetching entity mapping for identifier: {identifier}")
        token = RestService.get_service_account_token(
            config_id="ENTITY_SVC_CLIENT_ID", config_secret="ENTITY_SVC_CLIENT_SECRET"
        )
        new_url = f"{current_app.config.get('LEGAL_API_URL')}{current_app.config.get('LEGAL_API_VERSION_2')}"
        endpoint = f"{new_url}/businesses/search/affiliation_mappings"
        try:
            response = RestService.post(endpoint, token=token, data={"identifiers": [identifier]})
            logger.debug(f"Response: {response.json()}")
            return response.json().get("entityDetails")
        except HTTPError as http_error:
            # If this fails, we should still allow affiliation search to continue.
            logger.error("Failed to get affiliations mappings for identifier: %s", identifier)
            logger.error(http_error)
