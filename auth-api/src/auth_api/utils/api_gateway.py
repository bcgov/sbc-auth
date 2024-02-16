# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""helper to create api gateway client user."""
import secrets
import uuid


def generate_client_representation(account_id: int, client_id_pattern: str, env: str) -> dict:
    """Return dictionary for api gateway client user."""
    _id = str(uuid.uuid4())
    _secret = secrets.token_urlsafe(36)
    if env != 'prod':
        client_id_pattern += '-sandbox'
    _client_id = client_id_pattern.format(account_id=account_id)

    client_json: dict = {
        'id': _id,
        'clientId': _client_id,
        'rootUrl': '',
        'adminUrl': '',
        'baseUrl': '',
        'surrogateAuthRequired': False,
        'enabled': True,
        'alwaysDisplayInConsole': False,
        'clientAuthenticatorType': 'client-secret',
        'secret': _secret,
        'redirectUris': [
        ],
        'webOrigins': [
        ],
        'notBefore': 0,
        'bearerOnly': False,
        'consentRequired': False,
        'standardFlowEnabled': False,
        'implicitFlowEnabled': False,
        'directAccessGrantsEnabled': False,
        'serviceAccountsEnabled': True,
        'publicClient': False,
        'frontchannelLogout': False,
        'protocol': 'openid-connect',
        'attributes': {
            'saml.assertion.signature': 'false',
            'saml.multivalued.roles': 'false',
            'saml.force.post.binding': 'false',
            'saml.encrypt': 'false',
            'saml.server.signature': 'false',
            'saml.server.signature.keyinfo.ext': 'false',
            'exclude.session.state.from.auth.response': 'false',
            'client_credentials.use_refresh_token': 'false',
            'saml_force_name_id_format': 'false',
            'saml.client.signature': 'false',
            'tls.client.certificate.bound.access.tokens': 'false',
            'saml.authnstatement': 'false',
            'display.on.consent.screen': 'false',
            'saml.onetimeuse.condition': 'false'
        },
        'authenticationFlowBindingOverrides': {},
        'fullScopeAllowed': True,
        'nodeReRegistrationTimeout': -1,
        'protocolMappers': [
            {
                'name': 'Client ID',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-usersessionmodel-note-mapper',
                'consentRequired': False,
                'config': {
                    'user.session.note': 'clientId',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'clientId',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'preferred_username',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-hardcoded-claim-mapper',
                'consentRequired': False,
                'config': {
                    'claim.value': _client_id,
                    'userinfo.token.claim': 'true',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'preferred_username',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'family name',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-usermodel-property-mapper',
                'consentRequired': False,
                'config': {
                    'userinfo.token.claim': 'true',
                    'user.attribute': 'lastName',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'lastname',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'full name',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-hardcoded-claim-mapper',
                'consentRequired': False,
                'config': {
                    'claim.value': _client_id,
                    'userinfo.token.claim': 'true',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'name',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'username',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-hardcoded-claim-mapper',
                'consentRequired': False,
                'config': {
                    'claim.value': _client_id,
                    'userinfo.token.claim': 'true',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'username',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'given name',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-hardcoded-claim-mapper',
                'consentRequired': False,
                'config': {
                    'claim.value': _client_id,
                    'userinfo.token.claim': 'true',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'lastname',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'name',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-hardcoded-claim-mapper',
                'consentRequired': False,
                'config': {
                    'claim.value': _client_id,
                    'userinfo.token.claim': 'true',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'name',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'role list',
                'protocol': 'saml',
                'protocolMapper': 'saml-role-list-mapper',
                'consentRequired': False,
                'config': {
                    'single': 'false',
                    'attribute.nameformat': 'Basic',
                    'attribute.name': 'Role'
                }
            },
            {
                'name': 'realm roles',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-usermodel-realm-role-mapper',
                'consentRequired': False,
                'config': {
                    'multivalued': 'true',
                    'userinfo.token.claim': 'false',
                    'id.token.claim': 'false',
                    'access.token.claim': 'true',
                    'claim.name': 'roles',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'aud-account-services-mapper',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-audience-mapper',
                'consentRequired': False,
                'config': {
                    'id.token.claim': 'false',
                    'access.token.claim': 'true',
                    'included.custom.audience': 'account-services',
                    'userinfo.token.claim': 'false'
                }
            },
            {
                'name': 'aud-ppr-services-mapper',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-audience-mapper',
                'consentRequired': False,
                'config': {
                    'id.token.claim': 'false',
                    'access.token.claim': 'true',
                    'included.custom.audience': 'ppr-services',
                    'userinfo.token.claim': 'false'
                }
            },
            {
                'name': 'idp_userid',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-hardcoded-claim-mapper',
                'consentRequired': False,
                'config': {
                    'claim.value': _client_id,
                    'userinfo.token.claim': 'true',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'idp_userid',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'email',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-usermodel-property-mapper',
                'consentRequired': False,
                'config': {
                    'userinfo.token.claim': 'true',
                    'user.attribute': 'email',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'email',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'Source Mapper',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-hardcoded-claim-mapper',
                'consentRequired': False,
                'config': {
                    'claim.value': 'API_GW',
                    'userinfo.token.claim': 'false',
                    'id.token.claim': 'false',
                    'access.token.claim': 'true',
                    'claim.name': 'loginSource',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'aud-entity-services-mapper',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-audience-mapper',
                'consentRequired': False,
                'config': {
                    'id.token.claim': 'false',
                    'access.token.claim': 'true',
                    'included.custom.audience': 'entity-services',
                    'userinfo.token.claim': 'false'
                }
            },
            {
                'name': 'Client IP Address',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-usersessionmodel-note-mapper',
                'consentRequired': False,
                'config': {
                    'user.session.note': 'clientAddress',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'clientAddress',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'Client Host',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-usersessionmodel-note-mapper',
                'consentRequired': False,
                'config': {
                    'user.session.note': 'clientHost',
                    'id.token.claim': 'true',
                    'access.token.claim': 'true',
                    'claim.name': 'clientHost',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'AccountId',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-hardcoded-claim-mapper',
                'consentRequired': False,
                'config': {
                    'claim.value': str(account_id),
                    'userinfo.token.claim': 'false',
                    'id.token.claim': 'false',
                    'access.token.claim': 'true',
                    'claim.name': 'Account-Id',
                    'jsonType.label': 'String'
                }
            },
            {
                'name': 'aud-business-search-services-mapper',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-audience-mapper',
                'consentRequired': False,
                'config': {
                    'included.client.audience': 'business-search-service',
                    'id.token.claim': 'false',
                    'access.token.claim': 'true'
                }
            }
        ],
        'defaultClientScopes': [
            'web-origins',
            'roles'
        ],
        'optionalClientScopes': [
        ]
    }
    return client_json
