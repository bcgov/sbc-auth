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
import datetime

from notify_api.core import config as app_config
from notify_api.db.models.notification_status import NotificationStatusEnum

from notify_service.worker import cb_subscription_handler, job_handler, qsm


async def queue_worker(event_loop):
    """Run monitor Nats queue for email."""
    await qsm.run(loop=event_loop,
                  config=app_config,
                  callback=cb_subscription_handler)


async def pending_job_worker():
    """Run handle send PENDING email job every 5 minutes."""
    while True:
        await asyncio.sleep(app_config.PENDING_EMAIL_TIME_FRAME)
        await job_handler(NotificationStatusEnum.PENDING)


async def failure_job_worker():
    """Run handle resend FAILURE email job every 10 minutes."""
    while True:
        await asyncio.sleep(app_config.FAILURE_EMAIL_TIME_FRAME)
        await job_handler(NotificationStatusEnum.FAILURE)


async def archive_job_worker(dt):
    """Run handle archive delieved email job every day."""
    while True:
        now = datetime.datetime.now()
        remaining = (dt - now).total_seconds()
        if remaining < 86400:
            break
        # asyncio.sleep doesn't like long sleeps, so don't sleep more
        # than a day at a time
        await asyncio.sleep(86400)
        await job_handler(NotificationStatusEnum.DELIVERED)

if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()

    tasks = [asyncio.Task(queue_worker(event_loop)),
             asyncio.Task(pending_job_worker()),
             asyncio.Task(failure_job_worker())]
    event_loop.run_until_complete(asyncio.gather(*tasks))

    try:
        event_loop.run_forever()
    finally:
        event_loop.close()
