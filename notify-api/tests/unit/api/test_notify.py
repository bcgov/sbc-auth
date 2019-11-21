from notify_api.db.models.notification import NotificationModel
from tests.utilities.factory_scenarios import NOTIFICATION_DATA, NOTIFICATION_REQUEST_DATA


def test_get_by_id(session, app, client):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)
    res = client.get('/api/v1/notify/{}'.format(notification.id))
    response_data = res.json()
    assert res.status_code == 200
    assert notification.recipients == response_data['recipients']


def test_get_by_id_not_found(session, app, client):
    res = client.get('/api/v1/notify/{}'.format(int(1)))
    assert res.status_code == 404


def test_get_by_status(session, app, client):
    notification = NotificationModel(**NOTIFICATION_DATA[0])
    session.add(notification)
    session.commit()
    notification = session.merge(notification)
    res = client.get('/api/v1/notify/notifications/{}'.format(notification.status_code))
    response_data = res.json()
    assert res.status_code == 200
    assert notification.recipients == response_data[0]['recipients']


def test_post(session, app, client):
    res = client.post('/api/v1/notify/', json=NOTIFICATION_REQUEST_DATA[0])
    assert res.status_code == 200

    response_data = res.json()
    notification = session.query(NotificationModel).get(response_data['id'])
    assert notification.id == response_data['id']
