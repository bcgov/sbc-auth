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
"""Model for all activity stream related changes.

"""
from sqlalchemy import Column, Integer, String

from .base_model import BaseModel
from .db import db


class ActivityLog(BaseModel):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Model for ActivityLog Org record."""

    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True)
    actor = Column(String(250))  # who did the activity
    action = Column(String(250), index=True)  # Reset Passcode , Remove Affiliation etc
    item_type = Column(String(250), index=True)  # Org ,Business
    item_name = Column(String(250), index=True)  # UI needs to display this ;mostly org name/business name
    item_id = Column(Integer)  # id of the entity
    remote_addr = Column(String(250), index=False)

    @classmethod
    def fetch_activity_logs(cls, item_name: str, item_type: str,  # pylint:disable=too-many-arguments
                            action: str,
                            page: int, limit: int):
        """Fetch all activity logs."""
        query = db.session.query(ActivityLog)

        if item_name:
            query = query.filter(ActivityLog.item_name == item_name)
        if item_type:
            query = query.filter(ActivityLog.item_type == item_type)
        if action:
            query = query.filter(ActivityLog.action == action)

        # Add pagination
        pagination = query.paginate(per_page=limit, page=page)
        return pagination.items, pagination.total
