# Copyright © 2024 Province of British Columbia
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
"""Service for managing Simplified Organization data."""

from jinja2 import Environment, FileSystemLoader
from flask import current_app
from sqlalchemy import String, and_, func, or_

from auth_api.config import get_named_config
from auth_api.models import db
from auth_api.models import Org as OrgModel
from auth_api.models.dataclass import SimpleOrgSearch
from auth_api.schemas.simple_org import SimpleOrgInfoSchema
from auth_api.utils.converter import Converter


ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)
CONFIG = get_named_config()


class SimpleOrg:  # pylint: disable=too-few-public-methods
    """Manages a simplified version of organization data.

    This service supports searching organization data and returning a minimal data set.
    """

    def __init__(self, model):
        """Return a simple org service instance."""
        self._model = model

    @classmethod
    def search(cls, search_criteria: SimpleOrgSearch):
        """Search org records and returned a simplified result set."""
        current_app.logger.debug('<search')
        query = db.session.query(OrgModel)

        query = query.filter_conditionally(search_criteria.id, OrgModel.id, is_like=True)
        query = query.filter_conditionally(search_criteria.name, OrgModel.name, is_like=True)
        query = query.filter_conditionally(search_criteria.status, OrgModel.status_code)

        # OrgModel.branch_name default value is '', so we need to check for this
        if search_criteria.branch_name:
            query = query.filter(and_(OrgModel.branch_name != '',
                                      OrgModel.branch_name.ilike(f'%{search_criteria.branch_name}%')))

        # Use search_criteria.search_text to compare against id, name and branch name
        if search_criteria.search_text:
            search_text = f'%{search_criteria.search_text}%'
            query = query.filter(and_(
                or_(func.cast(OrgModel.id, String).ilike(search_text),
                    OrgModel.name.ilike(search_text),
                    and_(OrgModel.branch_name.ilike(search_text),
                         OrgModel.branch_name != ''))
            ))

        pagination = query.paginate(per_page=search_criteria.limit,
                                    page=search_criteria.page)

        org_list = [SimpleOrgInfoSchema.from_row(short_name) for short_name in pagination.items]
        converter = Converter()
        org_list = converter.unstructure(org_list)

        current_app.logger.debug('>search')
        return {
            'page': search_criteria.page,
            'limit': search_criteria.limit,
            'items': org_list,
            'total': pagination.total
        }
