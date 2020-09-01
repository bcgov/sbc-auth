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
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy import Integer, and_, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from auth_api.utils.enums import AccessType, Status, UserStatus
from .base_model import BaseModel
from .db import db
from .membership import Membership as MembershipModel
from .org import Org as OrgModel
from .user_status_code import UserStatusCode


class User(BaseModel):
    """This is the model for a User."""

    __tablename__ = 'user'

    __versioned__ = {
        'exclude': ['modified', 'modified_by_id', 'modified_by', 'created']
    }

    id = Column(Integer, primary_key=True)
    username = Column('username', String(100), index=True)
    firstname = Column('first_name', String(200), index=True)
    lastname = Column('last_name', String(200), index=True)
    email = Column('email', String(200), index=True)
    keycloak_guid = Column(
        'keycloak_guid', UUID(as_uuid=True), unique=True, nullable=True  # bcros users comes with no guid
    )
    roles = Column('roles', String(1000))
    is_terms_of_use_accepted = Column(Boolean(), default=False, nullable=True)
    terms_of_use_accepted_version = Column(
        ForeignKey('documents.version_id'), nullable=True
    )

    # a type for the user to identify what kind of user it is..ie anonymous , bcsc etc ..similar to login source
    type = Column('type', String(200), nullable=True)
    status = Column(ForeignKey('user_status_code.id'))
    idp_userid = Column('idp_userid', String(256), index=True)
    login_source = Column('login_source', String(200), nullable=True)
    login_time = Column(DateTime, default=None, nullable=True)

    contacts = relationship('ContactLink', primaryjoin='User.id == ContactLink.user_id', lazy='select')
    orgs = relationship('Membership',
                        primaryjoin='and_(User.id == Membership.user_id,  or_(Membership.status == ' + str(
                            Status.ACTIVE.value) + ', Membership.status == ' + str(
                                Status.PENDING_APPROVAL.value) + '))', lazy='select')  # noqa:E127

    terms_of_use_version = relationship('Documents', foreign_keys=[terms_of_use_accepted_version], uselist=False,
                                        lazy='select')
    user_status = relationship('UserStatusCode', foreign_keys=[status], lazy='subquery')

    @classmethod
    def find_by_username(cls, username):
        """Return the first user with the provided username."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_jwt_token(cls, token: dict):
        """Find an existing user by the keycloak GUID and (idpUserId is null or from token) in the provided token."""
        return db.session.query(User).filter(
            and_(User.keycloak_guid == token.get('sub'),
                 or_(User.idp_userid == token.get('idp_userid', None), User.idp_userid.is_(None)))).one_or_none()

    @classmethod
    def create_from_jwt_token(cls, token: dict, first_name: str, last_name: str):
        """Create a User from the provided JWT."""
        if token:
            user = User(
                username=token.get('preferred_username', None),
                firstname=first_name,
                lastname=last_name,
                email=token.get('email', None),
                keycloak_guid=token.get('sub', None),
                created=datetime.datetime.now(),
                roles=token.get('roles', None),
                login_source=token.get('loginSource', None)
            )
            current_app.logger.debug(
                'Creating user from JWT:{}; User:{}'.format(token, user)
            )
            user.status = UserStatusCode.get_default_type()
            user.idp_userid = token.get('idp_userid', None)
            user.login_time = datetime.datetime.now()
            user.save()
            return user
        return None

    @classmethod
    def update_from_jwt_token(cls, user, token: dict,  # pylint:disable=too-many-arguments
                              first_name: str, last_name: str, is_login: bool = False):
        """Update a User from the provided JWT."""
        if token is None or user is None:
            return None

        # Do not save if nothing has been changed
        # pylint: disable=too-many-boolean-expressions
        if not is_login \
                and user.username == token.get('preferred_username', user.username) \
                and user.firstname == first_name \
                and user.lastname == last_name \
                and user.email == token.get('email', user.email) \
                and str(user.keycloak_guid) == token.get('sub', user.keycloak_guid) \
                and user.status == UserStatus.ACTIVE.value \
                and user.login_source == token.get('login_source', user.login_source) \
                and user.idp_userid == token.get('idp_userid', None):
            return user

        current_app.logger.debug(
            'Updating user from JWT:{}; User:{}'.format(token, user)
        )

        user.username = token.get('preferred_username', user.username)

        user.firstname = first_name
        user.lastname = last_name
        user.email = token.get('email', user.email)

        user.modified = datetime.datetime.now()
        user.roles = token.get('roles', user.roles)
        if token.get('accessType', None) == AccessType.ANONYMOUS.value:  # update kcguid for anonymous users
            user.keycloak_guid = token.get('sub', user.keycloak_guid)

        # If this user is marked as Inactive, this login will re-activate them
        user.status = UserStatus.ACTIVE.value
        user.login_source = token.get('login_source', user.login_source)

        # If this is a request during login, update login_time
        if is_login:
            user.login_time = datetime.datetime.now()

        user.idp_userid = token.get('idp_userid')

        cls.commit()

        return user

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

            cls.save(user)
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
