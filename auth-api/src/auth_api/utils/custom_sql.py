# Copyright © 2019 Province of British Columbia
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
"""This manages custom object definition.

This can be used to define any view/materialized view/stored procedure/function etc.
"""


class CustomSql:  # pylint:disable=too-few-public-methods
    """This is the object for custom Sql definition."""

    def __init__(self, name, sql):
        self.name = name
        self.sql = sql
