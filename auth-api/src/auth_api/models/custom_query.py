# Copyright © 2023 Province of British Columbia
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
# pylint: disable=W0223
"""Custom Query class to extend BaseQuery class functionality."""

from datetime import date, datetime

from flask_sqlalchemy.query import Query
from sqlalchemy import and_, func


class CustomQuery(Query):  # pylint: disable=too-many-ancestors
    """Custom Query class to extend the base query class for helper functionality."""

    def filter_boolean(self, search_criteria, model_attribute):
        """Add query filter for boolean value."""
        if search_criteria is False:
            return self
        if search_criteria is None:
            raise ValueError("Invalid search criteria None, not True or False")
        return self.filter(model_attribute == search_criteria)

    def filter_conditionally(self, search_criteria, model_attribute, is_like: bool = False):
        """Add query filter if present."""
        if search_criteria is None:
            return self

        if isinstance(search_criteria, datetime):
            return self.filter(func.DATE(model_attribute) == search_criteria.date())
        if isinstance(search_criteria, date):
            return self.filter(func.DATE(model_attribute) == search_criteria)
        if is_like:
            # Ensure any updates for this kind of LIKE searches are using SQL Alchemy functions as it uses
            # bind variables to mitigate SQL Injection
            return self.filter(func.lower(model_attribute).ilike(f"%{search_criteria}%"))

        return self.filter(model_attribute == search_criteria)

    def filter_conditional_date_range(self, start_date: date, end_date: date, model_attribute, cast_to_date=True):
        """Add query filter for a date range if present."""
        # Dates in DB are stored as UTC, you may need to take into account timezones and adjust the input dates
        # depending on the needs
        query = self

        if start_date and end_date:
            return query.filter(
                and_(
                    func.DATE(model_attribute) if cast_to_date else model_attribute >= start_date,
                    func.DATE(model_attribute) if cast_to_date else model_attribute <= end_date,
                )
            )

        if start_date:
            query = query.filter(func.DATE(model_attribute) if cast_to_date else model_attribute >= start_date)

        if end_date:
            query = query.filter(func.DATE(model_attribute) if cast_to_date else model_attribute <= end_date)

        return query
