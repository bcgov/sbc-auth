#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
"""Service for listening and handling Queue Messages.

This service registers interest in listening to a Queue and processing received messages.
"""
import asyncio
import functools
import getopt
import json
import os
import random
import signal
import sys
from datetime import datetime

from nats.aio.client import Client as NATS  # noqa N814; by convention the name is NATS
from stan.aio.client import Client as STAN  # noqa N814; by convention the name is STAN

from entity_queue_common.service_utils import error_cb, logger, signal_handler

from account_mailer.enums import MessageType


async def run(loop, payload: dict, is_replace: bool = False):  # pylint: disable=too-many-locals
    """Run the main application loop for the service.

    This runs the main top level service functions for working with the Queue.
    """
    # NATS client connections
    nc = NATS()
    sc = STAN()

    async def close():
        """Close the stream and nats connections."""
        await sc.close()
        await nc.close()

    # Connection and Queue configuration.
    def nats_connection_options():
        return {
            'servers': os.getenv('NATS_SERVERS', 'nats://127.0.0.1:4222').split(','),
            'io_loop': loop,
            'error_cb': error_cb,
            'name': os.getenv('NATS_CLIENT_NAME', 'entity.filing.tester')
        }

    def stan_connection_options():
        return {
            'cluster_id': os.getenv('NATS_CLUSTER_ID', 'test-cluster'),
            'client_id': str(random.SystemRandom().getrandbits(0x58)),
            'nats': nc
        }

    def subscription_options():
        return {
            'subject': os.getenv('NATS_SUBJECT', 'account.mailer'),
            'queue': os.getenv('NATS_QUEUE', 'account.mailer.worker'),
            'durable_name': os.getenv('NATS_QUEUE', 'account.mailer.worker') + '_durable'
        }

    try:
        # Connect to the NATS server, and then use that for the streaming connection.
        await nc.connect(**nats_connection_options())
        await sc.connect(**stan_connection_options())

        # register the signal handler
        for sig in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, sig),
                                    functools.partial(signal_handler, sig_loop=loop, sig_nc=nc, task=close)
                                    )
        payload_template: dict = {
            'specversion': '1.x-wip',
            'source': 'https://api.pay.bcregistry.gov.bc.ca/v1/accounts/1',
            'time': f'{datetime.now()}',
            'datacontenttype': 'application/json'
        }
        if is_replace:
            message_payload = payload
        else:
            message_payload = payload_template
            message_payload.update(payload)

        print('message_payload-->', message_payload)
        await sc.publish(subject=subscription_options().get('subject'),
                         payload=json.dumps(message_payload).encode('utf-8'))

    except Exception as e:  # pylint: disable=broad-except
        # TODO tighten this error and decide when to bail on the infinite reconnect
        logger.error(e)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:r", ["payload=", "replace="])
    except getopt.GetoptError as e:
        print(e)
        sys.exit(2)

    replace_payload: bool = False

    for opt, arg in opts:
        if opt == '-h':
            sys.exit()
        elif opt in ("-p", "--payload"):
            payload = json.loads(arg)
        elif opt in ("-r", "--id"):
            replace_payload = str(arg).lower() == 'true'

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run(event_loop, payload, replace_payload))

# Examples:
# Reset passcode : python3 q_cli.py -p '{"type":"bc.registry.auth.resetPasscode", "data":{"emailAddresses": "test@test.com", "passCode":"1234", "businessIdentifier":"CP1234", "businessName": "TEST", "isStaffInitiated":true}}'
# PAD Account create : python3 q_cli.py -p '{"type": "bc.registry.payment.padAccountCreate", "data": {"accountId": "1234", "accountName": "Test Account", "padTosAcceptedBy": "bcsc/rtyujkmnbv", "paymentInfo": {"bankInstitutionNumber": "001", "bankTransitNumber": "99000", "bankAccountNumber": "XXXX2345", "paymentStartDate": "2021-01-01", "bankName": "XXX"}}}'
# Product Approved Detailed : ./q_cli.py -p '{"type":"bc.registry.auth.productApprovedNotificationDetailed", "data":{"subjectDescriptor": "Manufactured Home Registry Qualified Supplier", "productAccessDescriptor": "Qualified Supplier", "categoryDescriptor": "the Manufactured Home Registry", "productName": "Manufactured Home Registry – Manufacturers", "emailAddresses": "odysseus@highwaythreesolutions.com", "isReapproved": false}}'
# Product Re-approved Detailed : ./q_cli.py -p '{"type":"bc.registry.auth.productApprovedNotificationDetailed", "data":{"subjectDescriptor": "Manufactured Home Registry Qualified Supplier", "productAccessDescriptor": "Qualified Supplier", "categoryDescriptor": "the Manufactured Home Registry", "productName": "Manufactured Home Registry – Manufacturers", "emailAddresses": "odysseus@highwaythreesolutions.com", "isReapproved": true}}'
# Product Rejected Detailed : ./q_cli.py -p '{"type":"bc.registry.auth.productRejectedNotificationDetailed", "data":{"subjectDescriptor": "Manufactured Home Registry Qualified Supplier", "productAccessDescriptor": "Qualified Supplier", "categoryDescriptor": "the Manufactured Home Registry", "productName": "Manufactured Home Registry – Manufacturers", "emailAddresses": "odysseus@highwaythreesolutions.com", "accessDisclaimer": true, "contactType": "BCREG", "remarks":"This is a rejection reason."}}'
# Product Confirmation : ./q_cli.py -p '{"type":"bc.registry.auth.productConfirmationNotification", "data":{"subjectDescriptor": "Manufactured Home Registry Qualified Supplier", "productAccessDescriptor": "Qualified Supplier", "categoryDescriptor": "the Manufactured Home Registry", "productName": "Manufactured Home Registry – Manufacturers", "emailAddresses": "odysseus@highwaythreesolutions.com", "contactType": "BCREG", "hasAgreementAttachment": true, "attachmentType": "QUALIFIED_SUPPLIER"}}'
