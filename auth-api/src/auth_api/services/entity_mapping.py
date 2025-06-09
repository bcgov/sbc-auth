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
from sqlalchemy import and_, case, func, or_, select
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

        If all these have the same affiliations to the same org:
            - Business identifier gets shown over TEMP and NR (TEMP and NR are hidden)
            - TEMP and NR are combined into 1 row
            - TEMP by itself can show up if there is no NR and no BUSINESS for it
            - NR by itself can show up if there is no TEMP and no BUSINESS for it

        If affiliations are distributed over other orgs:
            - EG. For Business Identifier Org 1, Temp Org 1, NR Org 2
            - fix_stale_affiliations should repoint the NR to the Business
            - but if this bad data shows up Org 1 would have business, Org 2 would have NR (without affiliation)
            - EG. For Temp Org 1, NR Org2
            - Temp would show on Org 1, NR would show on Org2
        """
        paginate_for_non_search = not any(
            [search_details.identifier, search_details.status, search_details.name, search_details.type]
        )

        org_id_int = int(org_id or -1)

        affiliated_identifiers_cte = (
            db.session.query(Entity.business_identifier)
            .join(AffiliationModel, AffiliationModel.entity_id == Entity.id)
            .filter(AffiliationModel.org_id == org_id_int)
            .cte("affiliated_identifiers")
        )

        filtered_mappings = (
            db.session.query(EntityMapping)
            .filter(
                or_(
                    EntityMapping.business_identifier.in_(select(affiliated_identifiers_cte.c.business_identifier)),
                    EntityMapping.bootstrap_identifier.in_(select(affiliated_identifiers_cte.c.business_identifier)),
                    EntityMapping.nr_identifier.in_(select(affiliated_identifiers_cte.c.business_identifier)),
                ),
                or_(
                    EntityMapping.business_identifier.is_(None),
                    EntityMapping.business_identifier.in_(select(affiliated_identifiers_cte.c.business_identifier)),
                ),
            )
            .subquery()
        )

        priority_case = case(
            (filtered_mappings.c.business_identifier.isnot(None), 1),
            (
                and_(
                    filtered_mappings.c.bootstrap_identifier.isnot(None), filtered_mappings.c.nr_identifier.isnot(None)
                ),
                2,
            ),
            (filtered_mappings.c.bootstrap_identifier.isnot(None), 3),
            (filtered_mappings.c.nr_identifier.isnot(None), 4),
            else_=5,
        ).label("priority")

        identifiers_case = case(
            (
                and_(
                    filtered_mappings.c.business_identifier.isnot(None),
                    filtered_mappings.c.business_identifier.in_(
                        select(affiliated_identifiers_cte.c.business_identifier)
                    ),
                ),
                array([filtered_mappings.c.business_identifier]),
            ),
            (
                and_(
                    filtered_mappings.c.bootstrap_identifier.isnot(None), filtered_mappings.c.nr_identifier.isnot(None)
                ),
                case(
                    (
                        and_(
                            filtered_mappings.c.bootstrap_identifier.in_(
                                select(affiliated_identifiers_cte.c.business_identifier)
                            ),
                            filtered_mappings.c.nr_identifier.in_(
                                select(affiliated_identifiers_cte.c.business_identifier)
                            ),
                        ),
                        array([filtered_mappings.c.bootstrap_identifier, filtered_mappings.c.nr_identifier]),
                    ),
                    (
                        filtered_mappings.c.bootstrap_identifier.in_(
                            select(affiliated_identifiers_cte.c.business_identifier)
                        ),
                        array([filtered_mappings.c.bootstrap_identifier]),
                    ),
                    (
                        filtered_mappings.c.nr_identifier.in_(select(affiliated_identifiers_cte.c.business_identifier)),
                        array([filtered_mappings.c.nr_identifier]),
                    ),
                ),
            ),
            (
                and_(
                    filtered_mappings.c.nr_identifier.isnot(None),
                    filtered_mappings.c.nr_identifier.in_(select(affiliated_identifiers_cte.c.business_identifier)),
                ),
                array([filtered_mappings.c.nr_identifier]),
            ),
            (
                and_(
                    filtered_mappings.c.bootstrap_identifier.isnot(None),
                    filtered_mappings.c.bootstrap_identifier.in_(
                        select(affiliated_identifiers_cte.c.business_identifier)
                    ),
                ),
                array([filtered_mappings.c.bootstrap_identifier]),
            ),
        ).label("identifiers")

        created_date_case = case(
            (filtered_mappings.c.business_identifier == Entity.business_identifier, AffiliationModel.created),
            (filtered_mappings.c.bootstrap_identifier == Entity.business_identifier, AffiliationModel.created),
            (filtered_mappings.c.nr_identifier == Entity.business_identifier, AffiliationModel.created),
        ).label("created_on")

        row_number_column = (
            func.row_number()
            .over(partition_by=identifiers_case, order_by=(priority_case.asc(), created_date_case.desc()))
            .label("row_number")
        )

        complete_mappings_cte = (
            db.session.query(filtered_mappings.c.nr_identifier)
            .join(Entity, Entity.business_identifier == filtered_mappings.c.business_identifier)
            .join(AffiliationModel, AffiliationModel.entity_id == Entity.id)
            .filter(
                filtered_mappings.c.business_identifier.isnot(None),
                filtered_mappings.c.bootstrap_identifier.isnot(None),
                filtered_mappings.c.nr_identifier.isnot(None),
                AffiliationModel.org_id == org_id_int,
                Entity.is_loaded_lear.is_(True),
            )
            .cte("complete_mappings")
        )

        subq = (
            db.session.query(identifiers_case, created_date_case, row_number_column)
            .select_from(filtered_mappings)
            .join(
                Entity,
                or_(
                    filtered_mappings.c.business_identifier == Entity.business_identifier,
                    filtered_mappings.c.bootstrap_identifier == Entity.business_identifier,
                    filtered_mappings.c.nr_identifier == Entity.business_identifier,
                ),
            )
            .join(AffiliationModel, AffiliationModel.entity_id == Entity.id)
            .filter(
                AffiliationModel.org_id == org_id_int,
                Entity.is_loaded_lear.is_(True),
                or_(
                    filtered_mappings.c.business_identifier.isnot(None),
                    filtered_mappings.c.nr_identifier.is_(None),
                    filtered_mappings.c.nr_identifier.not_in(select(complete_mappings_cte.c.nr_identifier)),
                ),
            )
        ).subquery()

        query = (
            db.session.query(subq.c.identifiers, subq.c.created_on)
            .filter(subq.c.row_number == 1)
            .order_by(subq.c.created_on.desc())
        )

        if paginate_for_non_search:
            query = query.offset((search_details.page - 1) * search_details.limit).limit(search_details.limit)

        data = query.all()
        return data

    @staticmethod
    def populate_affiliation_base(org_id: int, search_details: AffiliationSearchDetails):
        """Get entity details from the database and expand multiple identifiers into separate rows."""
        data = EntityMappingService.paginate_from_affiliations(org_id, search_details)

        affiliation_bases = [
            AffiliationBase(identifier=identifier, created=created)
            for identifiers, created in data
            for identifier in identifiers
        ]

        if current_app.config.get("AFFILIATION_DEBUG") is True:
            t_identifiers = [f'"{base.identifier}"' for base in affiliation_bases if base.identifier.startswith("T")]
            nr_identifiers = [f'"{base.identifier}"' for base in affiliation_bases if base.identifier.startswith("NR")]
            other_identifiers = [
                f'"{base.identifier}"'
                for base in affiliation_bases
                if not base.identifier.startswith("T") and not base.identifier.startswith("NR")
            ]
            logger.debug(f"T identifiers ({len(t_identifiers)}): {', '.join(t_identifiers)}")
            logger.debug(f"NR identifiers ({len(nr_identifiers)}): {', '.join(nr_identifiers)}")
            logger.debug(f"Other identifiers ({len(other_identifiers)}): {', '.join(other_identifiers)}")

        return affiliation_bases

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
            return response.json().get("entityDetails")
        except HTTPError as http_error:
            # If this fails, we should still allow affiliation search to continue.
            logger.error("Failed to get affiliations mappings for identifier: %s", identifier)
            logger.error(http_error)
        return None
