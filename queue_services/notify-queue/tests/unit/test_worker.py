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
"""The Test Suites to ensure that the worker is operating correctly."""
import asyncio
import random
from datetime import datetime, timedelta

import pytest
from notify_api.core import config as AppConfig
from notify_api.db.models.notification import NotificationModel
from notify_api.db.models.notification_contents import NotificationContentsModel
from notify_api.db.models.notification_status import NotificationStatusEnum
from notify_api.services.notify import NotifyService

from notify_service import worker
from notify_service.worker import app_config, cb_subscription_handler, qsm
from tests.utilities.factory_scenarios import CONTENT_DATA, NOTIFICATION_DATA
from tests.utilities.utils import helper_add_notification_to_queue, subscribe_to_queue


@pytest.mark.asyncio
async def test_process_notification(session, sendmail_mock):  # pylint: disable=unused-argument
    """Assert that notification can be process."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    content = NotificationContentsModel(**CONTENT_DATA[1], notification_id=notification.id)
    session.add(content)
    session.commit()

    await worker.process_notification(notification.id, session)

    notification_update: NotificationModel = await NotifyService.find_notification(session, notification.id)
    assert notification_update is not None
    assert notification_update.id == notification.id
    assert notification_update.status_code == NotificationStatusEnum.DELIVERED


@pytest.mark.asyncio
async def test_process_notification_sendmail_failed(session, sendmail_failed_mock):  # pylint: disable=unused-argument
    """Assert that notification can not be process due to smtp server issue."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    content = NotificationContentsModel(**CONTENT_DATA[1], notification_id=notification.id)
    session.add(content)
    session.commit()

    await worker.process_notification(notification.id, session)

    notification_update: NotificationModel = await NotifyService.find_notification(session, notification.id)
    assert notification_update is not None
    assert notification_update.id == notification.id
    assert notification_update.status_code == NotificationStatusEnum.FAILURE


@pytest.mark.asyncio
async def test_process_notification_delivered(session, sendmail_mock):  # pylint: disable=unused-argument
    """Assert that notification can not be skip due to DELIVERED status."""
    notification = NotificationModel(**NOTIFICATION_DATA[4])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    content = NotificationContentsModel(**CONTENT_DATA[0], notification_id=notification.id)
    session.add(content)
    session.commit()

    await worker.process_notification(notification.id, session)

    notification_update: NotificationModel = await NotifyService.find_notification(session, notification.id)
    assert notification_update is not None
    assert notification_update.id == notification.id
    assert notification_update.status_code == NotificationStatusEnum.DELIVERED


@pytest.mark.asyncio
async def test_process_notification_failed(session):
    """Assert that notification can not be process due to data issue."""
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    await worker.process_notification(notification.id, session)

    notification_update: NotificationModel = await NotifyService.find_notification(session, notification.id)
    assert notification_update is not None
    assert notification_update.id == notification.id
    assert notification_update.status_code == NotificationStatusEnum.FAILURE


@pytest.mark.asyncio
async def test_cb_subscription_handler(session,  # pylint: disable=too-many-arguments, too-many-locals
                                       sendmail_mock, stan_server, event_loop,  # pylint: disable=unused-argument
                                       notification_stan, future):
    """Assert that notification id can be retrieved and decoded from the Queue."""
    from entity_queue_common.service import ServiceWorker  # pylint: disable=import-outside-toplevel

    # vars
    uuid = str(random.SystemRandom().randint(0, 999999))
    notification_id = uuid
    notification_subject = f'test_subject.{uuid}'
    notification_queue = f'test_queue.{uuid}'
    notification_durable_name = f'test_durable.{uuid}'

    notification = NotificationModel(**NOTIFICATION_DATA[0])
    notification.id = notification_id
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    content = NotificationContentsModel(**CONTENT_DATA[0], notification_id=notification.id)
    session.add(content)
    session.commit()
    content = session.merge(content)

    # register the handler to test it
    notification_subject = await subscribe_to_queue(notification_stan,
                                                    notification_subject,
                                                    notification_queue,
                                                    notification_durable_name,
                                                    cb_subscription_handler)

    # file handler callback
    msgs = []

    async def cb_file_handler(msg):
        nonlocal msgs
        nonlocal future
        msgs.append(msg)
        if len(msgs) == 1:
            future.set_result(True)

    file_handler_subject = app_config.FILER_PUBLISH_OPTIONS['subject']
    await subscribe_to_queue(notification_stan,
                             file_handler_subject,
                             f'notification_queue.{file_handler_subject}',
                             f'notification_durable_name.{file_handler_subject}',
                             cb_file_handler)

    service_worker = ServiceWorker()
    service_worker.sc = notification_stan
    qsm.service = service_worker

    # add notification id to queue
    await helper_add_notification_to_queue(notification_stan, notification_subject, notification_id=notification_id)

    try:
        await asyncio.wait_for(future, 2, loop=event_loop)
    except Exception as err:  # pylint: disable=broad-except
        print(err)

    notification_update: NotificationModel = await NotifyService.find_notification(session, notification_id)
    assert notification_update is not None
    assert notification_update.id == notification.id
    assert notification_update.status_code == NotificationStatusEnum.DELIVERED


@pytest.mark.asyncio
async def test_job_handler(session, sendmail_mock):  # pylint: disable=unused-argument
    """Assert that the notification records can be retrieve by job handler."""
    for i in NOTIFICATION_DATA:
        notification = NotificationModel(**i)
        session.add(notification)
        session.commit()

        content = NotificationContentsModel(**CONTENT_DATA[0], notification_id=notification.id)
        session.add(content)
        session.commit()

    notification_status = NotificationStatusEnum.FAILURE

    await worker.job_handler(notification_status)

    hours: int = AppConfig.DELIVERY_FAILURE_RETRY_TIME_FRAME
    for i in NOTIFICATION_DATA:
        if i['status_code'] == notification_status \
                and (datetime.utcnow() - timedelta(hours=hours)) < i['request_date']:
            notification_update: NotificationModel = await NotifyService.find_notification(session, i['id'])
            assert notification_update is not None
            assert notification_update.id == i['id']
            assert notification_update.status_code == NotificationStatusEnum.DELIVERED
