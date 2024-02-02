# Copyright © 2024 Province of British Columbia
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
"""Custom Query class to extend BaseQuery class functionality."""
from datetime import date, datetime

from flask_sqlalchemy import BaseQuery
from sqlalchemy import String, func


class CustomQuery(BaseQuery):
    """Custom Query class to extend the base query class for helper functionality."""

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
            return self.filter(func.cast(model_attribute, String).ilike(f'%{search_criteria}%'))

        return self.filter(model_attribute == search_criteria)
