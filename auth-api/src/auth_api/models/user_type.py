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
"""This manages a User Type record."""

from sqlalchemy import Column, String

from .db import db, ma


class UserType(db.Model):
    """Used to hold the user type information for a User of this service."""

    __tablename__ = 'user_type'

    user_type_code = Column(String(20), primary_key=True)
    user_type_desc = Column(String(50))
    full_desc = Column(String(250))

    @classmethod
    def find_by_code(cls, code):
        """Return the oldest User type record for the provided user_type_code."""
        return cls.query.filter_by(user_type_code=code).first()

    @classmethod
    def find_by_name(cls, name):
        """Return the oldest User type record for the provided user_type_code."""
        return cls.query.filter_by(user_type_desc=name).first()

    def save(self):
        """Store the User type into the local cache."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Cannot delete User type code records."""
        return self


class UserSchema(ma.ModelSchema):
    """Used to manage the default mapping between JSON and Domain model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the Domain fields to a default schema."""

        model = UserType
