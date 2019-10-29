from datetime import datetime
from notify_api.db.models.notification import NotificationModel
from notify_api.db.models.notification_contents import NotificationContentsModel, NotificationContentsRequest
from notify_api.db.crud import notification_contents as NotificaitonContentsCRUD
from tests.utilities.factory_scenarios import NOTIFICATION_DATA, CONTENT_DATA


def test_find_content_by_id(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    content = NotificationContentsModel(**CONTENT_DATA[0], notification_id=notification.id)
    session.add(content)
    session.commit()
    content = session.merge(content)

    result = loop.run_until_complete(
        NotificaitonContentsCRUD.find_contents_by_id(session, content.id)
    )
    assert result == content
    assert result.id == CONTENT_DATA[0]['id']
    assert result.subject == CONTENT_DATA[0]['subject']


def test_find_content_by_notification_id(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    content = NotificationContentsModel(**CONTENT_DATA[0], notification_id=notification.id)
    session.add(content)
    session.commit()
    content = session.merge(content)

    result = loop.run_until_complete(
        NotificaitonContentsCRUD.find_contents_by_notification_id(session, notification.id)
    )
    assert result == content
    assert result.id == CONTENT_DATA[0]['id']
    assert result.subject == CONTENT_DATA[0]['subject']


def test_create_contents(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)
    content = NotificationContentsModel(**CONTENT_DATA[0])
    requestContent: NotificationContentsRequest = NotificationContentsRequest(subject=content.subject,
                                                                              body=content.body)

    result = loop.run_until_complete(
        NotificaitonContentsCRUD.create_contents(session, requestContent, notification_id=notification.id)
    )
    assert result.id == CONTENT_DATA[0]['id']
    assert result.subject == CONTENT_DATA[0]['subject']


def test_create_contents_with_attachment(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    requestContent = NotificationContentsRequest(subject=CONTENT_DATA[2]['subject'],
                                                 body=CONTENT_DATA[2]['body'],
                                                 attachmentName=CONTENT_DATA[2]['attachment_name'],
                                                 attachmentBytes=CONTENT_DATA[2]['attachment'],
                                                 attachmentUrl=CONTENT_DATA[2]['attachment_url'])
    result = loop.run_until_complete(
        NotificaitonContentsCRUD.create_contents(session, requestContent, notification_id=notification.id)
    )

    assert result.subject == CONTENT_DATA[2]['subject']
    assert result.attachment_name == CONTENT_DATA[2]['attachment_name']


def test_create_contents_with_attachment_url(session, loop):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)

    requestContent = NotificationContentsRequest(subject=CONTENT_DATA[1]['subject'],
                                                 body=CONTENT_DATA[1]['body'],
                                                 attachmentName=CONTENT_DATA[1]['attachment_name'],
                                                 attachmentBytes=CONTENT_DATA[1]['attachment'],
                                                 attachmentUrl=CONTENT_DATA[1]['attachment_url'])
    result = loop.run_until_complete(
        NotificaitonContentsCRUD.create_contents(session, requestContent, notification_id=notification.id)
    )

    assert result.subject == CONTENT_DATA[1]['subject']
    assert result.attachment_name == CONTENT_DATA[1]['attachment_name']
