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


async def run(loop, mode, auth_account_id, auth_account_name, auth_username, bank_number, bank_branch_number,
              bank_account_number, order_number, transaction_amount, transaction_id,
              transaction_time):  # pylint: disable=too-many-locals
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
        payload = None
        if mode == 'pad':
            payload = {
                'specversion': '1.x-wip',
                'type': 'bc.registry.payment.padAccountCreate',
                'source': 'https://api.pay.bcregistry.gov.bc.ca/v1/accounts/{pay_account.auth_account_id}',
                'id': f'{auth_account_id}',
                'time': f'{datetime.now()}',
                'datacontenttype': 'application/json',
                'data': {
                    'accountId': auth_account_id,
                    'accountName': auth_account_name,
                    'padTosAcceptedBy': auth_username,
                    'paymentInfo': {
                        'bankInstitutionNumber': bank_number,
                        'bankTransitNumber': bank_branch_number,
                        'bankAccountNumber': bank_account_number,
                        'paymentStartDate': '-----',
                        'bankName': 'XXX'
                    }
                }
            }
        elif mode == 'refund':
            payload = {
                'specversion': '1.x-wip',
                'type': 'bc.registry.payment.refundRequest',
                'source': 'https://api.pay.bcregistry.gov.bc.ca/v1/invoices/{invoice.id}',
                'id': transaction_id,
                'datacontenttype': 'application/json',
                'data': {
                    'identifier': auth_account_id,
                    'orderNumber': order_number,
                    'transactionDateTime': transaction_time,
                    'transactionAmount': f'${transaction_amount}',
                    'transactionId': transaction_id
                }
            }
        elif mode == 'acc_lock':
            payload = {
                'specversion': '1.x-wip',
                'type': f'{MessageType.NSF_UNLOCK_ACCOUNT.value}',
                'source': 'https://api.pay.bcregistry.gov.bc.ca/v1/invoices/{invoice.id}',
                'id': auth_account_id,
                'datacontenttype': 'application/json',
                'data': {
                    'accountId': auth_account_id,
                    'accountName': auth_account_name
                }
            }
        elif mode == 'acc_unlock':
            payload = {
                'specversion': '1.x-wip',
                'type': f'{MessageType.NSF_LOCK_ACCOUNT.value}',
                'source': 'https://api.pay.bcregistry.gov.bc.ca/v1/invoices/{invoice.id}',
                'id': auth_account_id,
                'datacontenttype': 'application/json',
                'data': {
                    'accountId': auth_account_id,
                    'accountName': auth_account_name
                }
            }
        elif mode == 'conf_per':
            payload = {
                'specversion': '1.x-wip',
                'type': f'{MessageType.ACCOUNT_CONFIRMATION_PERIOD_OVER.value}',
                'source': 'https://api.pay.bcregistry.gov.bc.ca/v1/invoices/{invoice.id}',
                'id': auth_account_id,
                'datacontenttype': 'application/json',
                'data': {
                    'accountId': auth_account_id,
                    'nsfFee': 30
                }
            }
        elif mode == 'pad_invoice':
            payload = {
                'specversion': '1.x-wip',
                'type': f'{MessageType.PAD_INVOICE_CREATED.value}',
                'source': 'https://api.pay.bcregistry.gov.bc.ca/v1/invoices/{invoice.id}',
                'id': auth_account_id,
                'datacontenttype': 'application/json',
                'data': {
                    'accountId': auth_account_id,
                    'nsfFee': 30,
                    'invoice_total': 100
                }
            }
        elif mode == 'admin_removed':
            payload = {
                'specversion': '1.x-wip',
                'type': f'{MessageType.ADMIN_REMOVED.value}',
                'source': 'https://api.auth.bcregistry.gov.bc.ca/v1/invoices/{invoice.id}',
                'id': auth_account_id,
                'datacontenttype': 'application/json',
                'data': {
                    'accountId': auth_account_id,
                    'recipientEmail': 'foo@bar.com'
                }
            }

        await sc.publish(subject=subscription_options().get('subject'),
                         payload=json.dumps(payload).encode('utf-8'))

    except Exception as e:  # pylint: disable=broad-except
        # TODO tighten this error and decide when to bail on the infinite reconnect
        logger.error(e)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:i:n:u:b:t:a:o:p:d:z:",
                                   ["mode=", "id=", "name=", "username=", "banknumber=", "transitnumber=",
                                    "accountnumber=", "ordernumber=", "amount=", "transactionid=", "transactiontime="])
    except getopt.GetoptError:
        print('q_cli.py -o <old_identifier> -n <new_identifier>')
        sys.exit(2)

    auth_account_name = bank_number = bank_branch_number = \
        bank_account_number = order_number = transaction_amount = transaction_id = auth_username = transaction_time = None

    for opt, arg in opts:
        if opt == '-h':
            print('q_cli.py -o <old_identifier> -n <new_identifier>')
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg  # pad confirmation - "pad", refund request - "refund", acc suspended - "acc_suspend", acc restored - "acc_restore"
        elif opt in ("-i", "--id"):
            auth_account_id = arg
        elif opt in ("-n", "--name"):
            auth_account_name = arg
        elif opt in ("-u", "--username"):
            auth_username = arg
        elif opt in ("-b", "--banknumber"):
            bank_number = arg
        elif opt in ("-t", "--transitnumber"):
            bank_branch_number = arg
        elif opt in ("-a", "--accountnumber"):
            bank_account_number = arg
        elif opt in ("-o", "--ordernumber"):
            order_number = arg
        elif opt in ("-p", "--amount"):
            transaction_amount = arg
        elif opt in ("-d", "--transactionid"):
            transaction_id = arg
        elif opt in ("-z", "--transactiontime"):
            transaction_time = arg

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(

        run(event_loop, mode, auth_account_id, auth_account_name, auth_username, bank_number,
            bank_branch_number, bank_account_number, order_number, transaction_amount, transaction_id,
            transaction_time))

# pad cmd --> python3 q_cli.py -m pad -i 10 -n TestAccount -b 088 -t 00277 -a 12874890
# refund cmd --> python3 q_cli.py -m refund -i 10 -o 67892 -p 25.33 -d 988
# account suspended cmd --> python3 q_cli.py -m acc_lock -i 4 -n SomeAccount
# account restored cmd --> python3 q_cli.py -m acc_unlock -i 4 -n SomeAccount
# account conf pver-- >  python3 q_cli.py -m conf_per -i 4
# account conf pver-- >  python3 q_cli.py -m pad_invoice -i 4
# account admin removal-- >  python3 q_cli.py -m admin_removed -i 4
