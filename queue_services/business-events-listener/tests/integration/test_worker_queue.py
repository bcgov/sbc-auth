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
"""Test Suite to ensure the worker routines are working as expected."""

import json

import pytest
from auth_api.models import Affiliation as AffiliationModel
from auth_api.models import Entity as EntityModel
from auth_api.models import Org as OrgModel
from auth_api.models import OrgStatus as OrgStatusModel
from auth_api.models import OrgType as OrgTypeModel
from entity_queue_common.service_utils import subscribe_to_queue
from requests.models import Response

from .utils import helper_add_event_to_queue


@pytest.mark.asyncio
async def test_events_listener_queue(app, session, stan_server, event_loop, client_id, events_stan, future,
                                     monkeypatch):
    """Assert that events can be retrieved and decoded from the Queue."""
    # Call back for the subscription
    from business_events_listener.worker import cb_nr_subscription_handler

    # 1. Create an Org
    # 2. Mock the rest service to return the invoices with the org created.
    # 3. Publish NR event and assert it's affiliated to the org.
    org = OrgModel(
        name='Test',
        org_type=OrgTypeModel.get_default_type(),
        org_status=OrgStatusModel.get_default_status()
    ).save()
    org_id = org.id

    events_subject = 'test_subject'
    events_queue = 'test_queue'
    events_durable_name = 'test_durable'

    nr_number = 'NR 1234'
    nr_state = 'DRAFT'

    # register the handler to test it
    await subscribe_to_queue(events_stan,
                             events_subject,
                             events_queue,
                             events_durable_name,
                             cb_nr_subscription_handler)

    # Mock the rest service response to return the org just created.
    def get_invoices_mock(nr_number, token):
        response_content = json.dumps({
            'invoices': [{
                'businessIdentifier': nr_number,
                'paymentAccount': {
                    'accountId': org_id
                }
            }]
        })

        response = Response()
        response.status_code = 200
        response._content = str.encode(response_content)
        return response

    monkeypatch.setattr('auth_api.services.rest_service.RestService.get', get_invoices_mock)

    # add an event to queue
    await helper_add_event_to_queue(events_stan, events_subject, nr_number, nr_state, 'TEST')

    # Query the affiliations and assert the org has affiliation for the NR.
    entity: EntityModel = EntityModel.find_by_business_identifier(nr_number)
    assert entity
    assert entity.pass_code_claimed
    affiliations: [AffiliationModel] = AffiliationModel.find_affiliations_by_org_id(org_id)
    assert len(affiliations) == 1
    assert affiliations[0].entity_id == entity.id
    assert affiliations[0].org_id == org_id

    # Publish message again and assert it doesn't create duplicate affiliation.
    await helper_add_event_to_queue(events_stan, events_subject, nr_number, nr_state, 'TEST')
    affiliations: [AffiliationModel] = AffiliationModel.find_affiliations_by_org_id(org_id)
    assert len(affiliations) == 1
