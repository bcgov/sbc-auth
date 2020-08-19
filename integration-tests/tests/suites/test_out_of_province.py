import datetime
import json
import requests
import pytest
import urllib.request

from tests.utilities.settings import get_test_data, setup_access_data


@pytest.mark.incremental
@pytest.mark.parametrize('login_session', setup_access_data('OUT_OF_PROVINCE', ['BCEID', 'STAFF']), indirect=True, scope='class')
@pytest.mark.usefixtures('setup_data')
class TestOutOfProvince:

    __test__ = True

    @pytest.mark.skip_access_type('STAFF')
    def test_get_last_terms(self, testing_config, logger):
        """Get last version of termofuse."""
        call_url = f'{testing_config.auth_api_url}/documents/termsofuse'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        response_json = response.json()
        testing_config.terms_version = response_json.get('versionId')

    @pytest.mark.skip_access_type('STAFF')
    def test_accept_terms(self, testing_config, logger):
        """Test accept termofuser."""
        input_data = json.dumps({'termsversion': testing_config.terms_version, 'istermsaccepted': True})
        call_url = f'{testing_config.auth_api_url}/users/@me'
        logger.debug(f'[ACTION] Patch {call_url} with {input_data}')
        response = requests.patch(call_url,
                                  headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                           'Content-Type': 'application/json'},
                                  data=input_data)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    def test_get_user_profile(self, testing_config, logger):
        """Test get user profile. After login, the user should be created in db."""
        response = requests.get(f'{testing_config.auth_api_url}/users/@me',
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.user_id = response_json.get('keycloakGuid')

    @pytest.mark.skip_access_type('STAFF')
    def test_upload_document(self, testing_config, logger):
        """Test get user profile."""
        # download file
        file_contents = None
        file_name = 'affidavit_v1.pdf'
        file_url = f'{testing_config.minio_api_url}/{file_name}'
        with urllib.request.urlopen(file_url) as response:
            file_contents = response.read()
        assert file_contents is not None

        # get file signatures
        call_url = f'{testing_config.auth_api_url}/documents/{file_name}/signatures'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        pre_signed_url = response_json.get('preSignedUrl')
        testing_config.document_key = response_json.get('key')

        # upload file
        upload_header = {'Content-Type': 'application/pdf',
                         'x-amz-meta-userid': f'{testing_config.user_id }',
                         'x-amz-meta-key': f'{testing_config.document_key}',
                         'Content-Disposition': f'attachment; filename${file_name}'}
        files = {f'{file_name}': file_contents}
        call_url = f'{pre_signed_url}'
        logger.debug(f'[ACTION] put {call_url}')
        response = requests.put(call_url,
                                files=files,
                                headers=upload_header)
        assert response.status_code == 200

        # Request URL: https://auth-api-dev.pathfinder.gov.bc.ca/api/v1/users/59a9612e-e752-4177-becd-d8a3c0c6115f/affidavits
        # Request Method: POST
        # Status Code: 200 OK

    @pytest.mark.skip_access_type('STAFF')
    def test_create_affidavits(self, testing_config, logger):
        """Test create affidavits."""
        org_data = get_test_data(testing_config.test_data['org'])
        address_data = get_test_data(testing_config.test_data['address'])
        input_data = json.dumps({
            'documentId': testing_config.document_key,
            'issuer': org_data['name'],
            'contact': address_data
        })
        call_url = f'{testing_config.auth_api_url}/users/{testing_config.user_id}/affidavits'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    @pytest.mark.skip_access_type('STAFF')
    def test_create_account(self, testing_config, logger):
        """Test create account."""
        org_data = get_test_data(testing_config.test_data['org'])
        address_data = get_test_data(testing_config.test_data['address'])
        input_data = json.dumps({
            'name': org_data['name'],
            'accessType': 'EXTRA_PROVINCIAL',
            'mailingAddress': address_data
        })
        call_url = f'{testing_config.auth_api_url}/orgs'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.org_id = response_json.get('id')

    @pytest.mark.skip_access_type('STAFF')
    def test_create_user_profile(self, testing_config, logger):
        """Test create user profile (contact information)."""
        input_data = json.dumps(get_test_data(testing_config.test_data['user_profile']))
        call_url = f'{testing_config.auth_api_url}/users/contacts'
        logger.debug(f'[ACTION] Post {call_url} with {input_data}')
        response = requests.post(call_url,
                                 headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                          'Content-Type': 'application/json'},
                                 data=input_data)
        assert response.status_code == 201
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    @pytest.mark.skip_access_type('STAFF')
    def test_get_account(self, testing_config, logger):
        """Test get account."""
        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
        response_json = response.json()
        testing_config.org_type = response_json.get('orgType')

    def test_get_user_settings(self, testing_config, logger):
        """Test get user settings."""
        call_url = f'{testing_config.auth_api_url}/users/{testing_config.user_id}/settings'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    @pytest.mark.skip_access_type('STAFF')
    def test_get_membership(self, testing_config, logger):
        """Test get membership."""
        call_url = f'{testing_config.auth_api_url}/users/orgs/{testing_config.org_id}/membership'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members?status=ACTIVE'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs/{testing_config.org_id}/members?status=PENDING_APPROVAL'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    @pytest.mark.skip_access_type('BCEID')
    def test_get_accounts_by_staff(self, testing_config, logger):
        """Test get accounts by staff."""
        call_url = f'{testing_config.auth_api_url}/users/orgs?status=PENDING_AFFIDAVIT_REVIEW'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs?status=ACTIVE&page=1&limit=10'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs?status=REJECTED'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

        call_url = f'{testing_config.auth_api_url}/orgs?status=PENDING_ACTIVATION'
        logger.debug(f'[ACTION] Get {call_url}')
        response = requests.get(call_url,
                                headers={'Authorization': f'Bearer {testing_config.keycloak_token}'})
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')

    @pytest.mark.skip_access_type('BCEID')
    def test_approve_account(self, testing_config, tested_user, logger):
        """Test approved account by staff."""
        input_data = json.dumps({
            'statusCode': 'APPROVED'
        })
        call_url = f'{testing_config.auth_api_url}/orgs/{tested_user.config[0].org_id}/status'
        logger.debug(f'[ACTION] Patch {call_url} with {input_data}')
        response = requests.patch(call_url,
                                  headers={'Authorization': f'Bearer {testing_config.keycloak_token}',
                                           'Content-Type': 'application/json'},
                                  data=input_data)
        assert response.status_code == 200
        logger.debug(f'[ACTION] Response: {response.status_code} {response.json()}')
