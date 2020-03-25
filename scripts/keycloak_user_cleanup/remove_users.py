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
"""Job to remove keycloak users from auth upstream realm."""

import argparse

import requests


def run(env: str, idp_client_id: str, idp_client_secret: str, idp_realm: str, kc_client_id: str, kc_client_secret: str,
        kc_realm: str, excluded_usernames: list):
    if not idp_client_secret or not kc_client_secret:
        print('\n*********** ERROR ***********')
        print('Please provide client secret')
        print('*****************************\n')
        return

    env = env.lower()

    env_prefix = '' if env == 'prod' else f'-{env}'
    idp_base_url = f'https://auth-keycloak{env_prefix}.pathfinder.gov.bc.ca/auth/'
    kc_base_url = f'https://sso{env_prefix}.pathfinder.gov.bc.ca/auth/'

    idp_token_url = f'{idp_base_url}realms/{idp_realm}/protocol/openid-connect/token'
    kc_token_url = f'{kc_base_url}realms/{kc_realm}/protocol/openid-connect/token'

    response = requests.post(idp_token_url,
                             data=f'client_id={idp_client_id}&client_secret={idp_client_secret}&grant_type=client_credentials',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'})
    idp_admin_token = response.json().get('access_token')

    response = requests.post(kc_token_url,
                             data=f'client_id={kc_client_id}&client_secret={kc_client_secret}&grant_type=client_credentials',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'})
    kc_admin_token = response.json().get('access_token')

    get_users_url = f'{idp_base_url}admin/realms/{idp_realm}/users'
    response = requests.get(get_users_url, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {idp_admin_token}'
    })
    print('\n****************************************')
    print('Found {} users in realm {}'.format(len(response.json()), idp_realm))
    print('****************************************')

    delete_count: int = 0

    for user in response.json():
        user_id = user.get('id')
        user_name = user.get('username')
        get_role_mappings_url = f'{idp_base_url}admin/realms/{idp_realm}/users/{user_id}/role-mappings'
        response = requests.get(get_role_mappings_url, headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {idp_admin_token}'
        })
        is_excluded_user = user_name in excluded_usernames
        if response.json().get('realmMappings'):
            for role_mapping in response.json().get('realmMappings'):
                if role_mapping.get('name', None) == 'admin':
                    is_excluded_user = True

        if is_excluded_user:
            print('Excluding {}'.format(user_name))

        if not is_excluded_user:
            print('Deleting {} - START'.format(user_name))
            delete_users_url = f'{idp_base_url}admin/realms/{idp_realm}/users/{user_id}'
            requests.delete(delete_users_url, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {idp_admin_token}'
            })

            get_user_url = f'{kc_base_url}admin/realms/{kc_realm}/users?username={user_name}'
            response = requests.get(get_user_url, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {kc_admin_token}'
            })

            for kc_user in response.json():
                if kc_user.get('username') == f'bcros/{user_name}':
                    print('Deleting KC User {}'.format(kc_user.get('username')))
                    kc_user_id = kc_user.get('id')
                    delete_users_url = f'{kc_base_url}admin/realms/{kc_realm}/users/{kc_user_id}'
                    requests.delete(delete_users_url, headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {kc_admin_token}'
                    })

            delete_count += 1
            print('Deleting {} - DONE'.format(user_name))

    print('\n****************************************')
    print(f'* Deleted {delete_count} Users *')
    print('****************************************')


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Delete users from keycloak realm.")

    parser.add_argument("-env", "--env", dest="env", help="Environment [dev, test, prod]", metavar="ENV", default="dev")

    parser.add_argument("-idp_client", "--idp_client", dest="idp_client",
                        help="Service account client ID in updtream IDP", metavar="CLIENT",
                        default="auth-service-account")

    parser.add_argument("-idp_secret", "--idp_secret", dest="idp_secret",
                        help="Service account client secret in updtream IDP", metavar="SECRET")
    parser.add_argument("-idp_realm", "--idp_realm", dest="idp_realm", help="IDP realm", metavar="REALM",
                        default="master")

    parser.add_argument("-kc_client", "--kc_client", dest="kc_client", help="Service account client ID in Keycloak",
                        metavar="CLIENT",
                        default="sbc-auth-admin")
    parser.add_argument("-kc_secret", "--kc_secret", dest="kc_secret", help="Service account client secret in Keycloak",
                        metavar="SECRET")
    parser.add_argument("-kc_realm", "--kc_realm", dest="kc_realm", help="Keycloak realm", metavar="REALM",
                        default="fcf0kpqr")

    parser.add_argument("-exclude", "--exclude", dest="exclude", help="Comma separated value of excluded usernames",
                        metavar="EXCLUDE", default="")

    args = parser.parse_args()

    print(args)

    run(args.env, args.idp_client, args.idp_secret, args.idp_realm, args.kc_client, args.kc_secret, args.kc_realm,
        args.exclude.split(',') if args.exclude else [])
