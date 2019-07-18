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
"""This manages a User record in the Auth service.

A User stores basic information from a KeyCloak user (including the KeyCloak GUID).
"""

from flask import current_app

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, Integer, String

from .db import db, ma


class User(db.Model):
    """This is the model for a User."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column("username", String(100), index=True)
    firstname = Column("first_name", String(200), index=True)
    lastname = Column("last_name", String(200), index=True)
    email = Column("email", String(200), index=True)
    keycloak_guid = Column(
        "keycloak_guid", UUID(as_uuid=True), unique=True, nullable=False
    )
    created = Column(DateTime)
    modified = Column(DateTime)

    @classmethod
    def find_by_keycloak_guid(cls, keycloak_guid):
        """Return the first user with the provided KeyCloak GUID."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid).first()

    @classmethod
    def find_by_jwt_token(cls, token: dict):
        """Return if they exist and match the provided JWT."""
        return cls.query.filter_by(
            username=token.get("preferred_username", None)
        ).one_or_none()

    @classmethod
    def create_from_jwt_token(cls, token: dict):
        """Create a User from the provided JWT."""
        if token:
            user = User(
                username=token.get("preferred_username", None),
                roles=token.get("realm_access", None).get("roles", None),
                firstname=token.get("firstname", None),
                lastname=token.get("lastname", None),
                email=token.get("email", None),
                keycloak_guid=token.get("sub", None),
            )
            current_app.logger.debug(
                "Creating user from JWT:{}; User:{}".format(token, user)
            )
            db.session.add(user)
            db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        """Return the first User for the provided username."""
        return cls.query.filter_by(username=username).first()

    def save(self):
        """Saves the User model."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Users cannot be deleted so intercept the ORM by just returning."""
        return self


class UserSchema(ma.ModelSchema):
    """This is the Schema for a User model."""

    class Meta:
        """Maps all of the User fields to a default schema."""

        model = User
