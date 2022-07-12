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
"""This module holds data classes."""

from typing import List
from attr import dataclass, field


@dataclass
class Activity:
    """Used for Activity Log Publisher."""

    org_id: int
    action: str
    name: str
    value: str = None
    id: int = None
    type: str = None
    actor_id: id = None


@dataclass
class OrgSearch:  # pylint: disable=too-many-instance-attributes
    """Used for searching organizations."""

    name: str
    branch_name: str
    business_identifier: str
    statuses: List[str] = field()
    access_type: List[str] = field()
    bcol_account_id: str
    id: str
    decision_made_by: str
    org_type: str
    page: int
    limit: int
