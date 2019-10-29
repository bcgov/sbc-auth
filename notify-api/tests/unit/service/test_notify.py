from datetime import datetime

from notify_api.db.models.notification import NotificationModel, NotificationRequest, NotificationUpdate
from notify_api.services.notify import NotifyService
from tests.utilities.factory_scenarios import NOTIFICATION_DATA, NOTIFICATION_REQUEST_DATA


def test_find_notification_by_id(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotifyService.find_notification(session, notification.id)
    )
    assert result == notification
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']


def test_find_notification_by_status(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotifyService.find_notifications_by_status(session, notification.status_code)
    )
    assert result[0] == notification
    assert result[0].id == NOTIFICATION_DATA[0]['id']
    assert result[0].recipients == NOTIFICATION_DATA[0]['recipients']


def test_find_notification_by_status_time(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[2])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    result = loop.run_until_complete(
        NotifyService.find_notifications_by_status(session, notification.status_code)
    )
    assert result[0] == notification
    assert result[0].id == NOTIFICATION_DATA[2]['id']
    assert result[0].recipients == NOTIFICATION_DATA[2]['recipients']


def test_create_notification(session, loop):
    result = loop.run_until_complete(
        NotifyService.send_notification(session, NotificationRequest(**NOTIFICATION_REQUEST_DATA[0]))
    )
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']


def test_update_notification(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    updateNotification: NotificationUpdate = NotificationUpdate(id=notification.id,
                                                                sent_date=datetime.now(),
                                                                notify_status='FAILURE')
    result = loop.run_until_complete(
        NotifyService.update_notification_status(session, updateNotification)
    )
    assert result == notification
    assert result.id == NOTIFICATION_DATA[0]['id']
    assert result.recipients == NOTIFICATION_DATA[0]['recipients']
    assert result.status_code == 'FAILURE'


def test_update_notification_no_exists(session, loop):
    updateNotification: NotificationUpdate = NotificationUpdate(id=999,
                                                                sent_date=datetime.now(),
                                                                notify_status='FAILURE')
    result = loop.run_until_complete(
        NotifyService.update_notification_status(session, updateNotification)
    )
    assert result is None
