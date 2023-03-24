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
"""Constants definitions."""

# Group names
GROUP_PUBLIC_USERS = 'public_users'
GROUP_ACCOUNT_HOLDERS = 'account_holders'
GROUP_ANONYMOUS_USERS = 'anonymous_users'
GROUP_GOV_ACCOUNT_USERS = 'gov_account_users'
GROUP_API_GW_USERS = 'api_gateway_users'
GROUP_API_GW_SANDBOX_USERS = 'api_gateway_sandbox_users'

# Affidavit folder
AFFIDAVIT_FOLDER_NAME = 'Affidavits'

# BCol profile to product mapping, this will grow as and when more products are onboarded.
BCOL_PROFILE_PRODUCT_MAP = {
    'VS': 'VS',
    'PPR': 'RPPR',
    'RURLPROP': 'RPT',
    'MHR': 'MHR'
          # 'COURT_SERVICES': 'CSO',
          # "OSBR":'',
          #     "ADS",
          #     "COLIN_TYPE",
          #     "COMP",
          #     "ICBC",
          #     "MH",
          #     "LTO",
          #     "SES",
          #     "PPR",
          # "CCREF",
          # "CCREL",
          # "ATSOURCE",
          # "EMERGIS",
          # "LOCATION_CODE"
}
