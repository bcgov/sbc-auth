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

import datetime

from flask import current_app
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from auth_api.utils.roles import Status

from .base_model import BaseModel
from .db import db
from .membership import Membership as MembershipModel
from .org import Org as OrgModel


class User(BaseModel):
    """This is the model for a User."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column('username', String(100), index=True)
    firstname = Column('first_name', String(200), index=True)
    lastname = Column('last_name', String(200), index=True)
    email = Column('email', String(200), index=True)
    keycloak_guid = Column(
        'keycloak_guid', UUID(as_uuid=True), unique=True, nullable=False
    )
    roles = Column('roles', String(1000))

    contacts = relationship('ContactLink', back_populates='user', primaryjoin='User.id == ContactLink.user_id')
    orgs = relationship('Membership', back_populates='user',
                        primaryjoin='and_(User.id == Membership.user_id, \
                        or_(Membership.status == '+str(Status.ACTIVE.value)+', Membership.status == '+str(Status.PENDING_APPROVAL.value)+'))')

    is_terms_of_use_accepted = Column(Boolean(), default=False, nullable=True)
    terms_of_use_accepted_version = Column(
        ForeignKey('documents.version_id'), nullable=True
    )
    terms_of_use_version = relationship('Documents', foreign_keys=[terms_of_use_accepted_version], uselist=False,
                                        lazy='select')

    @classmethod
    def find_by_username(cls, username):
        """Return the first user with the provided username."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_jwt_token(cls, token: dict):
        """Find an existing user by the keycloak GUID in the provided token."""
        return cls.query.filter_by(
            keycloak_guid=token.get('sub', None)
        ).one_or_none()

    @classmethod
    def create_from_jwt_token(cls, token: dict):
        """Create a User from the provided JWT."""
        if token:
            user = User(
                username=token.get('preferred_username', None),
                firstname=token.get('firstname', None),
                lastname=token.get('lastname', None),
                email=token.get('email', None),
                keycloak_guid=token.get('sub', None),
                created=datetime.datetime.now(),
                roles=token.get('roles', None)
            )
            current_app.logger.debug(
                'Creating user from JWT:{}; User:{}'.format(token, user)
            )
            user.save()
            return user
        return None

    @classmethod
    def update_from_jwt_token(cls, token: dict, user):
        """Update a User from the provided JWT."""
        if token:
            if user:
                user.username = token.get('preferred_username', user.username)
                user.firstname = token.get('firstname', user.firstname)
                user.lastname = token.get('lastname', user.lastname)
                user.email = token.get('email', user.email)
                user.modified = datetime.datetime.now()
                user.roles = token.get('roles', user.roles)

                current_app.logger.debug(
                    'Updating user from JWT:{}; User:{}'.format(token, user)
                )
                cls.commit()
                return user
        return None

    @classmethod
    def find_users(cls, first_name, last_name, email):
        """Return a set of users with either the given username or the given email."""
        # TODO: This needs to be improved for scalability.  Paging large datasets etc.
        if first_name == '' and last_name == '' and email == '':
            return cls.query.all()
        return cls.query.filter(or_(cls.firstname == first_name, cls.lastname == last_name, cls.email == email)).all()

    @classmethod
    def update_terms_of_use(cls, token: dict, is_terms_accepted, terms_of_use_version):
        """Update the terms of service for the user."""
        if token:
            user = cls.find_by_jwt_token(token)
            user.is_terms_of_use_accepted = is_terms_accepted
            user.terms_of_use_accepted_version = terms_of_use_version

            current_app.logger.debug(
                'Updating users Terms of use is_terms_accepted:{}; terms_of_use_version:{}'.format(
                    is_terms_accepted, terms_of_use_version)
            )

            cls.commit()
            return user
        return None

    @classmethod
    def find_users_by_org_id_by_status_by_roles(cls, org_id, roles, status=Status.ACTIVE.value):
        """Find all members of the org with a status."""
        return db.session.query(User). \
            join(MembershipModel,
                 (User.id == MembershipModel.user_id) & (MembershipModel.status == status) &
                 (MembershipModel.membership_type_code.in_(roles))). \
            join(OrgModel).filter(OrgModel.id == org_id).all()

    def delete(self):
        """Users cannot be deleted so intercept the ORM by just returning."""
        return self
