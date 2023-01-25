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
"""Test suite for the integrations to NATS Queue."""


from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from auth_api.utils.enums import AccessType


def factory_org_model(org_name: str = 'Test ORg',
                      user_id=None):
    """Produce a templated org model."""
    org_type = OrgTypeModel.get_default_type()
    org_status = OrgStatusModel.get_default_status()
    org = OrgModel(name=org_name)
    org.org_type = org_type
    org.access_type = AccessType.REGULAR.value
    org.org_status = org_status
    org.created_by_id = user_id
    org.save()

    return org
