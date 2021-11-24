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
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, and_, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from auth_api.utils.enums import AccessType, LoginSource, Status, UserStatus
from auth_api.utils.roles import Role
from auth_api.utils.user_context import UserContext, user_context

from .base_model import BaseModel
from .db import db
from .membership import Membership as MembershipModel
from .org import Org as OrgModel
from .user_status_code import UserStatusCode


class User(BaseModel):
    """This is the model for a User."""

    __tablename__ = 'users'

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

    is_terms_of_use_accepted = Column(Boolean(), default=False, nullable=True)
    terms_of_use_accepted_version = Column(
        ForeignKey('documents.version_id'), nullable=True
    )

    # a type for the user to identify what kind of user it is..ie anonymous , bcsc etc ..similar to login source
    type = Column('type', String(200), nullable=True)
    status = Column(ForeignKey('user_status_codes.id'))
    idp_userid = Column('idp_userid', String(256), index=True)
    login_source = Column('login_source', String(200), nullable=True)
    login_time = Column(DateTime, default=None, nullable=True)
    verified = Column(Boolean())

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
    @user_context
    def find_by_jwt_token(cls, **kwargs):
        """Find an existing user by the keycloak GUID and (idpUserId is null or from token) in the provided token."""
        user_from_context: UserContext = kwargs['user_context']
        return db.session.query(User).filter(
            and_(User.keycloak_guid == user_from_context.sub,
                 or_(User.idp_userid == user_from_context.token_info.get('idp_userid', None),
                     User.idp_userid.is_(None)))).one_or_none()

    @classmethod
    @user_context
    def create_from_jwt_token(cls, first_name: str, last_name: str, **kwargs):
        """Create a User from the provided JWT."""
        user_from_context: UserContext = kwargs['user_context']
        token = user_from_context.token_info
        if token:
            user = User(
                username=user_from_context.user_name,
                firstname=first_name,
                lastname=last_name,
                email=token.get('email', None),
                keycloak_guid=user_from_context.sub,
                created=datetime.datetime.now(),
                login_source=user_from_context.login_source,
                status=UserStatusCode.get_default_type(),
                idp_userid=token.get('idp_userid', None),
                login_time=datetime.datetime.now(),
                type=cls._get_type(user_from_context=user_from_context),
                verified=cls._is_verified(user_from_context.login_source)
            )
            current_app.logger.debug(f'Creating user from JWT:{token}; User:{user}')

            user.save()
            return user
        return None

    @classmethod
    @user_context
    def update_from_jwt_token(cls, user,  # pylint:disable=too-many-arguments
                              first_name: str, last_name: str, is_login: bool = False, **kwargs):
        """Update a User from the provided JWT."""
        user_from_context: UserContext = kwargs['user_context']
        token = user_from_context.token_info
        if not token or not user:
            return None

        # Do not save if nothing has been changed
        # pylint: disable=too-many-boolean-expressions
        if not is_login \
                and (user.username == user_from_context.user_name or user.username) \
                and user.firstname == first_name \
                and user.lastname == last_name \
                and user.email == token.get('email', user.email) \
                and (str(user.keycloak_guid) == user_from_context.sub or user.keycloak_guid) \
                and user.status == UserStatus.ACTIVE.value \
                and (user.login_source == user_from_context.login_source or user.login_source) \
                and user.idp_userid == token.get('idp_userid', None):
            return user

        current_app.logger.debug(f'Updating user from JWT:{token}; User:{user}')
        user.username = user_from_context.user_name or user.username

        user.firstname = first_name
        user.lastname = last_name
        user.email = token.get('email', user.email)

        user.modified = datetime.datetime.now()

        if token.get('accessType', None) == AccessType.ANONYMOUS.value:  # update kcguid for anonymous users
            user.keycloak_guid = user_from_context.sub or user.keycloak_guid

        # If this user is marked as Inactive, this login will re-activate them
        user.status = UserStatus.ACTIVE.value
        user.login_source = user_from_context.login_source or user.login_source
        user.type = cls._get_type(user_from_context)

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
    @user_context
    def update_terms_of_use(cls, is_terms_accepted, terms_of_use_version, **kwargs):
        """Update the terms of service for the user."""
        user_from_context: UserContext = kwargs['user_context']
        if user_from_context.token_info:
            user = cls.find_by_jwt_token()
            user.is_terms_of_use_accepted = is_terms_accepted
            user.terms_of_use_accepted_version = terms_of_use_version

            current_app.logger.debug(f'Updating users Terms of use is_terms_accepted:{is_terms_accepted}; '
                                     f'terms_of_use_version:{terms_of_use_version}')

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

    @classmethod
    def _get_type(cls, user_from_context: UserContext) -> str:
        """Return type of the user from the token info."""
        user_type: str = None
        if user_from_context.roles:
            if Role.ANONYMOUS_USER.value in user_from_context.roles \
                    or user_from_context.login_source == LoginSource.BCROS.value:
                user_type = Role.ANONYMOUS_USER.name
            elif Role.GOV_ACCOUNT_USER.value in user_from_context.roles:
                user_type = Role.GOV_ACCOUNT_USER.name
            elif Role.PUBLIC_USER.value in user_from_context.roles \
                    or user_from_context.login_source in [LoginSource.BCEID.value, LoginSource.BCSC.value]:
                user_type = Role.PUBLIC_USER.name
            elif user_from_context.is_staff():
                user_type = Role.STAFF.name
            elif user_from_context.is_system():
                user_type = Role.SYSTEM.name

        return user_type

    @classmethod
    def _is_verified(cls, login_source):
        """Return if user is a verified user by checking login source."""
        return login_source == LoginSource.BCSC.value
