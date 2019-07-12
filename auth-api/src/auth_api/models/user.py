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
"""This manages a User record in the Auth service."""

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, Integer, String

from .db import db, ma

class User(db.Model):
    """This is the User model for the Auth service."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column('username', String(100), index=True)
    first_name = Column('first_name', String(200), index=True)
    last_name = Column('last_name', String(200), index=True)
    email = Column('email', String(200), index=True)
    keycloak_guid = Column('keycloak_guid', UUID(as_uuid=True), unique=True, nullable=False)
    creation_date = Column(DateTime(True))

    @classmethod
    def find_by_keycloak_guid(cls, keycloak_guid):
        """Return the first user with the provided KeyCloak GUID."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid).first()

    @classmethod
    def find_by_jwt_token(cls, token: dict):
        """Return if they exist and match the provided JWT."""
        return cls.query.filter_by(username=token.get('preferred_username', None)).one_or_none()

    @classmethod
    def create_from_jwt_token(cls, token: dict):
        """Create a User from the provided JWT."""
        if token:
            user = User(
                username
            )

class UserSchema(ma.ModelSchema):
    """Used to manage the default mapping between JSON and User model."""

    class Meta:
        """Maps all of the User fields to a default schema."""

        model = User
