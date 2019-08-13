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
"""Super class to handle all operations related to base model."""

import datetime
from flask import g
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from .db import db


class BaseModel(db.Model):
    """This class manages all of the base model functions."""

    __abstract__ = True

    @declared_attr
    def created_by_id(cls):  # pylint:disable=no-self-argument
        return Column(ForeignKey('user.id'), default=cls.get_current_user)

    @declared_attr
    def modified_by_id(cls):  # pylint:disable=no-self-argument
        return Column(ForeignKey('user.id'), onupdate=cls.get_current_user)

    @declared_attr
    def created_by(cls):  # pylint:disable=no-self-argument
        return relationship('User', foreign_keys=[cls.created_by_id], uselist=False)

    @declared_attr
    def modified_by(cls):  # pylint:disable=no-self-argument
        return relationship('User', foreign_keys=[cls.modified_by_id], uselist=False)

    @staticmethod
    def get_current_user():
        from .user import User as UserModel
        token = g.jwt_oidc_token_info
        user = UserModel.find_by_jwt_token(token)
        return user.id

    created = Column(DateTime, default=datetime.datetime.now)
    modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def commit():
        """Commit the session."""
        db.session.commit()

    def flush(self):
        """Save and flush."""
        db.session.add(self)
        db.session.flush()
        return self

    def save(self):
        """Save and commit."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete and commit."""
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def rollback():
        """RollBack."""
        db.session.rollback()
