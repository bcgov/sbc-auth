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
"""This manages a User record.
"""
from flask import current_app

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from .db import db, ma


class Users(db.Model):
    """Used to hold the audit information for a User of this service."""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, server_default=text("nextval('users_id_seq'::regclass)"))
    username = Column(String(100), unique=True)
    passwd = Column(String(100))
    firstname = Column(String(100))
    lastname = Column(String(200))
    display_name = Column(String(254))
    email = Column(String(254))
    user_source = Column(String(20))
    user_type_code = Column(ForeignKey('user_type.user_type_code'))
    sub = Column(String(36), unique=True)
    iss = Column(String(1024))
    creation_date = Column(DateTime(True))

    user_type = relationship('UserType')

    @classmethod
    def find_by_username(cls, username):
        """Return the first user record for the provided username."""
        return cls.query.filter_by(username=username).first()

    def save(self):
        """Store the User into the local cache."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Cannot delete User records."""
        return self
        # need to intercept the ORM and stop Users from being deleted

    @classmethod
    def find_by_jwt_token(cls, token: dict):
        """Return a User if they exist and match the provided JWT."""
        return cls.query.filter_by(username=token.get('preferred_username', None)).one_or_none()

    @classmethod
    def create_from_jwt_token(cls, token: dict):
        """Create a user record from the provided JWT token.

        Use the values found in the vaild JWT for the realm
        to populate the User audit data
        """
        if token:
            # TODO: schema doesn't parse from token need to figure that out ... LATER!
            # s = KeycloakUserSchema()
            # u = s.load(data=token, partial=True)
            user = Users(
                username=token.get('preferred_username', None),
                firstname=token.get('given_name', None),
                lastname=token.get('family_name', None),
                display_name=token.get('name', None),
                email=token.get('email', None),
                user_source=token.get('preferred_username', None),
                # user_type_code=token.get('realm_access', None).get('roles', None),
                sub=token.get('sub', None),
                iss=token.get('iss', None)
            )
            current_app.logger.debug('Creating user from JWT:{}; User:{}'.format(token, user))
            db.session.add(user)
            db.session.commit()
            return user
        return None


class UserSchema(ma.ModelSchema):
    """Used to manage the default mapping between JSON and Domain model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the Domain fields to a default schema."""

        model = Users
