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
"""s2i based launch script to run the service."""
import asyncio
import random
from copy import deepcopy

from business_events_listener.worker import APP_CONFIG, cb_nr_subscription_handler, qsm


if __name__ == '__main__':

    # my_config = config.get_named_config(os.getenv('DEPLOYMENT_ENV', 'production'))

    event_loop = asyncio.get_event_loop()


    async def event_subscriptions():
        """Run both nr and entity tasks."""
        nr_task = qsm.run(loop=event_loop,
                          config=APP_CONFIG,
                          callback=cb_nr_subscription_handler)

        subscriber_coroutines = [nr_task]

        res = await asyncio.gather(*subscriber_coroutines, return_exceptions=True)
        return res


    event_loop.run_until_complete(event_subscriptions())
    try:
        event_loop.run_forever()
    finally:
        event_loop.close()
