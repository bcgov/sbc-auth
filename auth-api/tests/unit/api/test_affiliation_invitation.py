# Copyright © 2023 Province of British Columbia
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

"""Tests to verify the invitations API end-point.

Test-Suite to ensure that the /affiliationsInvitations endpoint is working as expected.
"""
import json

import pytest

from auth_api import status as http_status
from auth_api.schemas import utils as schema_utils
from auth_api.services import AffiliationInvitation as AffiliationInvitationService
from auth_api.services.keycloak import KeycloakService
from tests.utilities.factory_scenarios import TestEntityInfo, TestJwtClaims, TestOrgInfo
from tests.utilities.factory_utils import factory_affiliation_invitation, factory_auth_header


KEYCLOAK_SERVICE = KeycloakService()


@pytest.mark.parametrize('from_org_info, to_org_info, entity_info, role, claims', [
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'ADMIN',
     TestJwtClaims.public_user_role),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'USER',
     TestJwtClaims.public_user_role),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'COORDINATOR',
     TestJwtClaims.public_user_role),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'ADMIN',
     TestJwtClaims.public_bceid_user),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'USER',
     TestJwtClaims.public_bceid_user),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'COORDINATOR',
     TestJwtClaims.public_bceid_user)
])
def test_add_affiliation_invitation(client, jwt, session, keycloak_mock, business_mock, stan_server,
                                    from_org_info, to_org_info, entity_info, role,
                                    claims):  # pylint:disable=unused-argument
    """Assert that an affiliation invitation can be POSTed."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock,
                                                                                             from_org_info,
                                                                                             to_org_info,
                                                                                             entity_info,
                                                                                             claims)

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
        headers=headers, content_type='application/json')
    dictionary = json.loads(rv_invitation.data)

    assert rv_invitation.status_code == http_status.HTTP_201_CREATED
    assert dictionary.get('token') is not None
    result_json = rv_invitation.json

    assert schema_utils.validate(result_json, 'affiliation_invitation_response')[0]
    assert result_json['fromOrg']
    assert result_json['fromOrg']['id'] == from_org_id
    assert result_json['toOrg']
    assert result_json['toOrg']['id'] == to_org_id
    assert result_json['businessIdentifier'] == business_identifier
    assert result_json['status'] == 'PENDING'

    # Defaults to EMAIL affiliation invitation type
    assert result_json['type'] == 'EMAIL'


@pytest.mark.parametrize('from_org_info, to_org_info, entity_info, role, claims', [
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'ADMIN',
     TestJwtClaims.public_user_role),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'USER',
     TestJwtClaims.public_user_role),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'COORDINATOR',
     TestJwtClaims.public_user_role),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'ADMIN',
     TestJwtClaims.public_bceid_user),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'USER',
     TestJwtClaims.public_bceid_user),
    (TestOrgInfo.affiliation_from_org, TestOrgInfo.affiliation_to_org, TestEntityInfo.entity_lear_mock, 'COORDINATOR',
     TestJwtClaims.public_bceid_user)
])
def test_add_affiliation_invitation_with_passcode(client, jwt, session, keycloak_mock, business_mock, stan_server,
                                                  from_org_info, to_org_info, entity_info, role,
                                                  claims):
    """Assert that an affiliation invitation can be POSTed."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock,
                                                                                             from_org_info,
                                                                                             to_org_info,
                                                                                             entity_info,
                                                                                             claims)

    invitation_payload = factory_affiliation_invitation(from_org_id=from_org_id,
                                                        to_org_id=to_org_id,
                                                        business_identifier=business_identifier)
    invitation_payload['passCode'] = entity_info['passCode']

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        invitation_payload), headers=headers, content_type='application/json')
    dictionary = json.loads(rv_invitation.data)

    assert rv_invitation.status_code == http_status.HTTP_201_CREATED
    assert dictionary.get('token') is not None
    result_json = rv_invitation.json

    assert schema_utils.validate(result_json, 'affiliation_invitation_response')[0]
    assert result_json['fromOrg']
    assert result_json['fromOrg']['id'] == from_org_id
    assert result_json['toOrg']
    assert result_json['toOrg']['id'] == to_org_id
    assert result_json['businessIdentifier'] == business_identifier
    assert result_json['status'] == 'ACCEPTED'
    assert result_json['type'] == 'PASSCODE'


def test_affiliation_invitation_already_exists(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that POSTing an already existing affiliation invitation returns a 400."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock)

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
        headers=headers, content_type='application/json')

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(from_org_id=from_org_id,
                                       to_org_id=to_org_id,
                                       business_identifier=business_identifier)),
                                headers=headers, content_type='application/json')

    assert rv_invitation.status_code == http_status.HTTP_400_BAD_REQUEST
    dictionary = json.loads(rv_invitation.data)
    assert dictionary['message'] == 'The data you want to insert already exists.'


def test_delete_affiliation_invitation(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that an affiliation invitation can be deleted."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock)

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
        headers=headers, content_type='application/json')

    invitation_dictionary = json.loads(rv_invitation.data)
    affiliation_invitation_id = invitation_dictionary['id']

    rv_invitation = client.delete('/api/v1/affiliationInvitations/{}'.format(affiliation_invitation_id),
                                  headers=headers, content_type='application/json')
    assert rv_invitation.status_code == http_status.HTTP_200_OK

    rv_invitation = client.get('/api/v1/affiliationInvitations/{}'.format(affiliation_invitation_id),
                               headers=headers, content_type='application/json')
    assert rv_invitation.status_code == http_status.HTTP_404_NOT_FOUND
    dictionary = json.loads(rv_invitation.data)
    assert dictionary['message'] == 'The requested affiliation invitation could not be found.'


def test_add_affiliation_invitation_invalid(client, jwt, session, business_mock):
    """Assert that POSTing an invalid affiliation invitation returns a 400."""
    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.public_user_role)
    rv = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=None,
            to_org_id=None,
            business_identifier=None)),
        headers=headers, content_type='application/json')
    assert rv.status_code == http_status.HTTP_400_BAD_REQUEST


def test_get_affiliation_invitation_by_id(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that an invitation can be retrieved."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock)

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
        headers=headers, content_type='application/json')

    invitation_dictionary = json.loads(rv_invitation.data)
    affiliation_invitation_id = invitation_dictionary['id']

    rv = client.get('/api/v1/affiliationInvitations/{}'.format(affiliation_invitation_id),
                    headers=headers, content_type='application/json')

    result_json = rv.json
    assert schema_utils.validate(result_json, 'affiliation_invitation_response')[0]
    assert rv.status_code == http_status.HTTP_200_OK
    assert result_json['id'] == affiliation_invitation_id


def test_update_affiliation_invitation(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that an affiliation invitation can be updated."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock)

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
        headers=headers, content_type='application/json')

    invitation_dictionary = json.loads(rv_invitation.data)
    affiliation_invitation_id = invitation_dictionary['id']

    updated_affiliation_invitation = {}

    rv_invitation = client.patch('/api/v1/affiliationInvitations/{}'.format(affiliation_invitation_id), data=json.dumps(
        updated_affiliation_invitation),
        headers=headers, content_type='application/json')

    result_json = rv_invitation.json

    assert rv_invitation.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(result_json, 'affiliation_invitation_response')[0]
    dictionary = json.loads(rv_invitation.data)
    assert dictionary['status'] == 'PENDING'


def test_expire_affiliation_invitation(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that an affiliation invitation can be expired."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock)

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
                                headers=headers, content_type='application/json')

    invitation_dictionary = json.loads(rv_invitation.data)
    affiliation_invitation_id = invitation_dictionary['id']

    updated_affiliation_invitation = {'status': 'EXPIRED'}

    rv_invitation = client.patch('/api/v1/affiliationInvitations/{}'.format(affiliation_invitation_id), data=json.dumps(
        updated_affiliation_invitation),
                                 headers=headers, content_type='application/json')

    result_json = rv_invitation.json

    assert rv_invitation.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(result_json, 'affiliation_invitation_response')[0]
    dictionary = json.loads(rv_invitation.data)
    assert dictionary['status'] == 'EXPIRED'


def test_accept_affiliation_invitation(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that an affiliation invitation can be accepted."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock)

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
        headers=headers, content_type='application/json')

    invitation_dictionary = json.loads(rv_invitation.data)
    affiliation_invitation_id = invitation_dictionary['id']

    affiliation_invitation_token = AffiliationInvitationService.generate_confirmation_token(affiliation_invitation_id,
                                                                                            from_org_id,
                                                                                            to_org_id,
                                                                                            business_identifier)

    assert affiliation_invitation_token is not None

    rv_invitation = client.put('/api/v1/affiliationInvitations/{}/token/{}'.format(affiliation_invitation_id,
                                                                                   affiliation_invitation_token),
                               headers=headers, content_type='application/json')

    dictionary = json.loads(rv_invitation.data)

    assert rv_invitation.status_code == http_status.HTTP_200_OK
    assert dictionary['status'] == 'ACCEPTED'

    rv_affiliations = client.get('/api/v1/orgs/{}/affiliations'.format(to_org_id), headers=headers)
    assert rv_affiliations.status_code == http_status.HTTP_200_OK

    assert schema_utils.validate(rv_affiliations.json, 'affiliations_response')[0]
    affiliations = json.loads(rv_affiliations.data)
    assert affiliations is not None
    assert affiliations['entities'][0]['businessIdentifier'] == business_identifier


def test_get_affiliation_invitations(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that affiliation invitations can be retrieved."""
    headers, from_org_id, to_org_id, business_identifier = \
        setup_affiliation_invitation_data(client, jwt, session, keycloak_mock)

    client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
                                headers=headers, content_type='application/json')

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    rv_invitations = client.get('/api/v1/affiliationInvitations?fromOrgId={}'.format(from_org_id),
                                headers=headers,
                                content_type='application/json')

    result_json = rv_invitations.json

    assert rv_invitations.status_code == http_status.HTTP_200_OK
    assert result_json['affiliationInvitations']
    assert len(result_json['affiliationInvitations']) == 1


def setup_affiliation_invitation_data(client, jwt, session, keycloak_mock,
                                      from_org_info=TestOrgInfo.affiliation_from_org,
                                      to_org_info=TestOrgInfo.affiliation_to_org,
                                      entity_info=TestEntityInfo.entity_lear_mock,
                                      claims=TestJwtClaims.public_user_role):  # pylint:disable=unused-argument
    """Set up seed data for an affiliation invitation."""
    headers = factory_auth_header(jwt=jwt, claims=claims)
    client.post('/api/v1/users', headers=headers, content_type='application/json')
    rv_from_org = client.post('/api/v1/orgs', data=json.dumps(from_org_info),
                              headers=headers, content_type='application/json')
    rv_to_org = client.post('/api/v1/orgs', data=json.dumps(to_org_info),
                            headers=headers, content_type='application/json')

    headers_entity = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)
    rv_entity = client.post('/api/v1/entities', data=json.dumps(entity_info),
                            headers=headers_entity, content_type='application/json')

    dictionary_from_org = json.loads(rv_from_org.data)
    dictionary_to_org = json.loads(rv_to_org.data)
    dictionary_entity = json.loads(rv_entity.data)

    from_org_id = dictionary_from_org['id']
    to_org_id = dictionary_to_org['id']
    business_identifier = dictionary_entity['businessIdentifier']

    client.post('/api/v1/orgs/{}/affiliations'.format(from_org_id), headers=headers,
                data=json.dumps(
                    {'businessIdentifier': business_identifier,
                     'passCode': entity_info['passCode']}), content_type='application/json')

    return headers, from_org_id, to_org_id, business_identifier


def _get_entity_json_for_post(counter):
    return {'businessIdentifier': f'CP000{counter}',
            'businessNumber': f'791861078BC{counter}',
            'name': f'Testing entity {counter}',
            'passCode': '222222222', 'corpTypeCode': 'CP'}


def setup_additional_affiliation_invitation_data(client, jwt, session, keycloak_mock,
                                                 claims=TestJwtClaims.public_user_role,
                                                 new_org_count=5,
                                                 new_entity_count=1
                                                 ):  # pylint:disable=unused-argument
    """Set up additional data for testing affiliation invitations."""
    headers = factory_auth_header(jwt=jwt, claims=claims)
    headers_entity = factory_auth_header(jwt=jwt, claims=TestJwtClaims.passcode)

    new_org_ids = []
    new_entity_business_identifiers = []

    for i in range(new_org_count):
        new_org_json = client.post('/api/v1/orgs', data=json.dumps({'name': f'Test Affiliation Invitation Org {i}'}),
                                   headers=headers, content_type='application/json')
        new_org: dict = json.loads(new_org_json.data)
        new_org_ids.append(new_org.get('id'))

    for i in range(new_entity_count):
        new_entity_info = _get_entity_json_for_post(i)
        client.post('/api/v1/entities', data=json.dumps(new_entity_info),
                    headers=headers_entity, content_type='application/json')

        new_entity_business_identifiers.append(new_entity_info['businessIdentifier'])

    return new_org_ids, new_entity_business_identifiers


def test_authorize_affiliation_invitation(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that an affiliation invitation (type REQUEST) can be authorized."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock)

    rv_invitation = client.post('/api/v1/affiliationInvitations', data=json.dumps(
        factory_affiliation_invitation(
            from_org_id=from_org_id,
            to_org_id=to_org_id,
            business_identifier=business_identifier)),
        headers=headers, content_type='application/json')

    invitation_dictionary = json.loads(rv_invitation.data)
    affiliation_invitation_id = invitation_dictionary['id']

    rv_invitation = client.patch(f'/api/v1/affiliationInvitations/{affiliation_invitation_id}/authorization/accept',
                                 headers=headers,
                                 content_type='application/json')

    result_json = rv_invitation.json

    assert rv_invitation.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(result_json, 'affiliation_invitation_response')[0]
    dictionary = json.loads(rv_invitation.data)
    assert dictionary['status'] == 'ACCEPTED'


def test_reject_authorize_affiliation_invitation(client, jwt, session, keycloak_mock, business_mock, stan_server):
    """Assert that an affiliation invitation (type REQUEST) can be refused to be authorized."""
    headers, from_org_id, to_org_id, business_identifier = setup_affiliation_invitation_data(client,
                                                                                             jwt,
                                                                                             session,
                                                                                             keycloak_mock)
    # create affiliation invitation in test
    sample_invite = factory_affiliation_invitation(
        from_org_id=from_org_id,
        to_org_id=to_org_id,
        business_identifier=business_identifier)

    rv_invitation = client.post(
        '/api/v1/affiliationInvitations',
        data=json.dumps(sample_invite),
        headers=headers, content_type='application/json'
    )

    invitation_dictionary = json.loads(rv_invitation.data)
    affiliation_invitation_id = invitation_dictionary['id']

    rv_invitation = client.patch(f'/api/v1/affiliationInvitations/{affiliation_invitation_id}/authorization/refuse',
                                 headers=headers,
                                 content_type='application/json')

    result_json = rv_invitation.json

    assert rv_invitation.status_code == http_status.HTTP_200_OK
    assert schema_utils.validate(result_json, 'affiliation_invitation_response')[0]
    dictionary = json.loads(rv_invitation.data)
    assert dictionary['status'] == 'FAILED'


def _create_affiliations_for_test(client, headers,
                                  org_id1, org_id2, org_id3, org_id4,
                                  business_identifier1, business_identifier2):
    sample_invites = [
        factory_affiliation_invitation(
            from_org_id=org_id1,
            to_org_id=org_id2,
            business_identifier=business_identifier1,
            affiliation_invitation_type='REQUEST'
        ),
        factory_affiliation_invitation(
            from_org_id=org_id2,
            to_org_id=org_id3,
            business_identifier=business_identifier1,
            affiliation_invitation_type='REQUEST'),
        factory_affiliation_invitation(
            from_org_id=org_id3,
            to_org_id=org_id4,
            business_identifier=business_identifier1,
            affiliation_invitation_type='REQUEST'),
        factory_affiliation_invitation(
            from_org_id=org_id4,
            to_org_id=org_id1,
            business_identifier=business_identifier1,
            affiliation_invitation_type='REQUEST'),
        factory_affiliation_invitation(
            from_org_id=org_id4,
            to_org_id=org_id1,
            business_identifier=business_identifier2,
            affiliation_invitation_type='REQUEST')]

    # create affiliation invitation in test
    for i in range(len(sample_invites)):
        data = json.dumps(sample_invites[i])
        client.post(
            '/api/v1/affiliationInvitations',
            data=data,
            headers=headers, content_type='application/json')


def test_getting_affiliation_invitations_for_the_org(app, client, jwt, session, keycloak_mock, business_mock,
                                                     stan_server):
    """Assert that correct count of affiliation invitations is returned for provided org id."""
    orig_val_max_number_of_orgs = app.config.get('MAX_NUMBER_OF_ORGS')
    app.config.update(MAX_NUMBER_OF_ORGS=10)
    # setup all the required data
    headers, org_id_0a, org_id_0b, business_identifier = setup_affiliation_invitation_data(client,
                                                                                           jwt,
                                                                                           session,
                                                                                           keycloak_mock)
    new_org_ids, new_business_identifiers = setup_additional_affiliation_invitation_data(client,
                                                                                         jwt,
                                                                                         session,
                                                                                         keycloak_mock)

    _create_affiliations_for_test(client, headers,
                                  org_id1=new_org_ids[0],
                                  org_id2=new_org_ids[1],
                                  org_id3=new_org_ids[2],
                                  org_id4=new_org_ids[3],
                                  business_identifier1=business_identifier,
                                  business_identifier2=new_business_identifiers[0])

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    expected_org_id = new_org_ids[0]
    url = f'/api/v1/affiliationInvitations?orgId={expected_org_id}&businessDetails=True'
    affiliation_invitations_response = client.get(url, headers=headers)
    affiliation_invitations_dict: dict = json.loads(affiliation_invitations_response.data)
    affiliation_invitations = affiliation_invitations_dict['affiliationInvitations']

    assert len(affiliation_invitations) == 2   # should be two, one for 'toOrg' other for 'fromOrg'
    assert affiliation_invitations[0]['toOrg']['id'] == expected_org_id \
           or affiliation_invitations[0]['fromOrg']['id'] == expected_org_id
    assert affiliation_invitations[1]['toOrg']['id'] == expected_org_id \
           or affiliation_invitations[1]['fromOrg']['id'] == expected_org_id

    app.config.update(MAX_NUMBER_OF_ORGS=orig_val_max_number_of_orgs)


def test_getting_affiliation_invitations_sent_to_org_for_entity(app, client, jwt, session, keycloak_mock, business_mock,
                                                                stan_server):
    """Assert that correct count of affiliation invitations is returned for provided org id and business identifier."""
    # setup all the required data
    orig_val_max_number_of_orgs = app.config.get('MAX_NUMBER_OF_ORGS')
    app.config.update(MAX_NUMBER_OF_ORGS=10)
    headers, org_id_0a, org_id_0b, business_identifier = setup_affiliation_invitation_data(client,
                                                                                           jwt,
                                                                                           session,
                                                                                           keycloak_mock)
    new_org_ids, new_business_identifiers = setup_additional_affiliation_invitation_data(client,
                                                                                         jwt,
                                                                                         session,
                                                                                         keycloak_mock)

    _create_affiliations_for_test(client, headers,
                                  org_id1=new_org_ids[0],
                                  org_id2=new_org_ids[1],
                                  org_id3=new_org_ids[2],
                                  org_id4=new_org_ids[3],
                                  business_identifier1=business_identifier,
                                  business_identifier2=new_business_identifiers[0])

    headers = factory_auth_header(jwt=jwt, claims=TestJwtClaims.staff_admin_role)
    expected_org_id = new_org_ids[0]
    url = f'/api/v1/affiliationInvitations?toOrgId=' \
          f'{expected_org_id}&business_identifier={business_identifier}&businessDetails=True'
    affiliation_invitations_response = client.get(url, headers=headers)
    affiliation_invitations_dict: dict = json.loads(affiliation_invitations_response.data)
    affiliation_invitations = affiliation_invitations_dict['affiliationInvitations']

    assert len(affiliation_invitations) == 1  # should be only one to org and business identifier match
    assert affiliation_invitations[0]['toOrg']['id'] == expected_org_id
    assert affiliation_invitations[0]['entity']['businessIdentifier'] == business_identifier

    app.config.update(MAX_NUMBER_OF_ORGS=orig_val_max_number_of_orgs)
