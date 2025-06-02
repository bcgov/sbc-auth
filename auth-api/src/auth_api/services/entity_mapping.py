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
from sqlalchemy import and_, case, func, or_, text
from sqlalchemy.dialects.postgresql import array
from structured_logging import StructuredLogging

from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.dataclass import AffiliationBase, AffiliationSearchDetails
from auth_api.models.entity import Entity
from auth_api.models.entity_mapping import EntityMapping

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
    def from_entity_details(entity_details: dict):
        """Create and populate an EntityMapping object from entity details.
        
        Only updates an existing row if the new data fills in missing identifiers.
        Otherwise creates a new row.
        """
        nr_identifier = entity_details.get("nrNumber")
        bootstrap_identifier = entity_details.get("bootstrapIdentifier")
        business_identifier = entity_details.get("identifier")

        logger.debug(
            f"Upserting entity mapping with business_identifier: {business_identifier}, "
            f" bootstrap_identifier: {bootstrap_identifier}, nr_identifier: {nr_identifier}"
        )
        conditions = []
        if nr_identifier:
            conditions.append(EntityMapping.nr_identifier == nr_identifier)
        if bootstrap_identifier:
            conditions.append(EntityMapping.bootstrap_identifier == bootstrap_identifier)
        if business_identifier:
            conditions.append(EntityMapping.business_identifier == business_identifier)

        existing_mapping = db.session.query(EntityMapping).filter(or_(*conditions)).first()
        if existing_mapping:
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
                existing_mapping.save()
                return
            

        new_mapping = EntityMapping(
            nr_identifier=nr_identifier,
            bootstrap_identifier=bootstrap_identifier,
            business_identifier=business_identifier
        )
        new_mapping.save()
