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

"""Tests to assure the user end-point.

Test-Suite to ensure that the /user endpoint is working as expected.
"""

import json
import os

from auth_api import status as http_status
from auth_api.utils.roles import Role
from auth_api.exceptions.errors import Error
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.entity import Entity as EntityModel
from auth_api.models.org_type import OrgType as OrgTypeModel
from auth_api.models.org_status import OrgStatus as OrgStatusModel
from auth_api.models.payment_type import PaymentType as PaymentTypeModel
from auth_api.models.org import Org as OrgModel
from auth_api.models.user import User as UserModel
import datetime


token_header = {
    'alg': os.getenv('JWT_OIDC_ALGORITHMS'),
    'typ': 'JWT',
    'kid': os.getenv('JWT_OIDC_AUDIENCE')
}


def get_claims(role: str = Role.BASIC.value):
    """Return the claim with the role param."""
    claim = {
        'jti': 'a50fafa4-c4d6-4a9b-9e51-1e5e0d102878',
        'exp': 31531718745,
        'iat': 1531718745,
        'aud': 'sbc-auth-web',
        'typ': 'Bearer',
        'iss': os.getenv('JWT_OIDC_ISSUER'),
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'firstname': 'Test',
        'lastname': 'User',
        'username': 'testuser',
        'preferred_username': 'testuser',
        'realm_access':
        {
            'roles':
                [
                    '{}'.format(role)
                ]
        },
    }
    return claim


def get_claims_invalid(role: str = Role.BASIC.value):
    """Return the claim with the role param."""
    claim = {
        'firstname': 'Test',
        'lastname': 'User',
        'username': 'troublemaker',
        'jti': 'a50fafa4-c4d6-4a9b-9e51-1e5e0d102878',
        'exp': 31531718745,
        'iat': 1531718745,
        'iss': 'foobar',
        'aud': 'sbc-auth-web',
        'sub': 'barfoo',
        'typ': 'Bearer',
        'realm_access':
            {
                'roles':
                    [
                        '{}'.format(role)
                    ]
            },
        'preferred_username': 'cp1234567 '
    }
    return claim


def factory_entity_model():
    entity = EntityModel(business_identifier='CP1234567')
    entity.save()
    return entity


def factory_org_model(name, session):
    """Produce a templated org model."""
    org_type = OrgTypeModel(code='TEST', desc='Test')
    session.add(org_type)
    session.commit()

    org_status = OrgStatusModel(code='TEST', desc='Test')
    session.add(org_status)
    session.commit()

    preferred_payment = PaymentTypeModel(code='TEST', desc='Test')
    session.add(preferred_payment)
    session.commit()

    org = OrgModel(name=name)
    org.org_type = org_type
    org.org_status = org_status
    org.preferred_payment = preferred_payment
    org.save()

    return org


def factory_user_model():
    user = UserModel(
        username='testuser',
        firstname='Test',
        lastname='User',
        email='testuser@abc.com',
        keycloak_guid='15099883-3c3f-4b4c-a124-a1824d6cba84',
        created=datetime.datetime.now(),
        roles='basic'
    )
    user = user.save()
    return user


def factory_affiliation_model(entity_id, org_id):
    affiliation = AffiliationModel(entity=entity_id, org=org_id)
    affiliation.save()
    return affiliation


def test_add_affiliation(session, client, jwt):
    """Assert that the endpoint returns 201."""
    entity = factory_entity_model()

    entity_info = {
        'entity': entity.id
    }

    org = factory_org_model(name='My Test Affiliation', session=session)

    factory_user_model()

    token = jwt.create_jwt(get_claims(), token_header)
    # print("######################## token {}", token)
    headers = {'Authorization': f'Bearer {token}', 'content-type': 'application/json'}
    rv = client.post(f'/api/v1/orgs/' + str(org.id) + '/affiliations', data=json.dumps(entity_info),
                     headers=headers)

    assert rv.status_code == http_status.HTTP_201_CREATED


def test_add_affiliation_no_token_returns_401(session, client, jwt):
    """Assert that the endpoint returns 201."""
    entity = factory_entity_model()

    entity_info = {
        'entity': entity.id
    }

    org = factory_org_model(name='My Test Affiliation', session=session)

    rv = client.post(f'/api/v1/orgs/' + str(org.id) + '/affiliations', data=json.dumps(entity_info),
                     headers=None)

    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_add_affiliation_invalid_token_returns_401(session, client, jwt):
    """Assert that the endpoint returns 201."""
    entity = factory_entity_model()

    entity_info = {
        'entity': entity.id
    }

    org = factory_org_model(name='My Test Affiliation', session=session)

    token = jwt.create_jwt(get_claims_invalid(), token_header)
    headers = {'Authorization': f'Bearer {token}', 'content-type': 'application/json'}
    rv = client.post(f'/api/v1/orgs/' + str(org.id) + '/affiliations', data=json.dumps(entity_info),
                     headers=headers)

    assert rv.status_code == http_status.HTTP_401_UNAUTHORIZED


def test_get_affiliation(session, client, jwt):
    """Assert that the endpoint returns 200."""
    entity = factory_entity_model()

    entity_info = {
        'entity': entity.id
    }

    org = factory_org_model(name='My Test Affiliation', session=session)

    token = jwt.create_jwt(get_claims(), token_header)
    headers = {'Authorization': f'Bearer {token}', 'content-type': 'application/json'}
    rv = client.get(f'/api/v1/orgs/' + str(org.id) + '/affiliations', data=json.dumps(entity_info), headers=headers)

    assert rv.status_code == http_status.HTTP_200_OK


def test_get_affiliation_not_exist(session, client, jwt):
    """Assert that the endpoint returns data not found."""
    entity = factory_entity_model()

    entity_info = {
        'entity': entity.id
    }

    token = jwt.create_jwt(get_claims(), token_header)
    headers = {'Authorization': f'Bearer {token}', 'content-type': 'application/json'}
    rv = client.get(f'/api/v1/orgs/12345/affiliations', data=json.dumps(entity_info), headers=headers)

    assert rv.status_code == Error.DATA_NOT_FOUND.status_code


def test_update_affiliation(session, client, jwt):
    """Assert that the endpoint returns data not found."""
    entity = factory_entity_model()

    entity_info = {
        'entity': entity.id
    }

    org = factory_org_model(name='My Test Affiliation', session=session)

    affiliation = factory_affiliation_model(entity.id, org.id)

    token = jwt.create_jwt(get_claims(), token_header)
    headers = {'Authorization': f'Bearer {token}', 'content-type': 'application/json'}
    rv = client.put(f'/api/v1/orgs/' + str(org.id) + '/affiliations/' + str(affiliation.id), data=json.dumps(entity_info),
                    headers=headers)

    assert rv.status_code == http_status.HTTP_200_OK


def test_update_affiliation_invalid_entity_id(session, client, jwt):
    """Assert that the endpoint returns data not found."""
    entity = factory_entity_model()

    entity_info = {
        'entity': 12345
    }

    org = factory_org_model(name='My Test Affiliation', session=session)

    affiliation = factory_affiliation_model(entity.id, org.id)

    token = jwt.create_jwt(get_claims(), token_header)
    headers = {'Authorization': f'Bearer {token}', 'content-type': 'application/json'}
    rv = client.put(f'/api/v1/orgs/' + str(org.id) + '/affiliations/' + str(affiliation.id),
                    data=json.dumps(entity_info), headers=headers)

    assert rv.status_code == http_status.HTTP_404_NOT_FOUND