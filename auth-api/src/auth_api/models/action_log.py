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
"""This manages a action log record.
"""

from sqlalchemy import Column, Date, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from .db import db, ma


class ActionLog(db.Model):
    """Used to hold the action type information for a User of this service."""
    __tablename__ = 'action_log'

    log_id = Column(Integer, primary_key=True, server_default=text("nextval('log_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.user_id'), nullable=False)
    action_code = Column(ForeignKey('action.action_code'), nullable=False)
    target_id = Column(Integer, nullable=False)
    target_type = Column(String(50), nullable=False)
    action_date = Column(Date, nullable=False)
    memo = Column(String(250))

    action = relationship('Action')
    user = relationship('User')

    @classmethod
    def find_by_user_id(cls, user_id):
        """Return the action record for the provided user_id."""
        return cls.query.filter_by(user_id=user_id)

    def save(self):
        """Store the action log into the local cache."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Cannot delete action log records."""
        return self


class UserSchema(ma.ModelSchema):
    """Used to manage the default mapping between JSON and Domain model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the Domain fields to a default schema."""

        model = ActionLog
