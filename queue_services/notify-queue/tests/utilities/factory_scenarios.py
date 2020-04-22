import base64

from datetime import datetime, timedelta
from notify_api.core import config as AppConfig

NOTIFICATION_DATA = [
    {
        'id': 1,
        'request_date': datetime.utcnow(),
        'recipients': 'aaa@aaa.com',
        'type_code': 'EMAIL',
        'status_code': 'PENDING'
    },
    {
        'id': 2,
        'request_date': datetime.utcnow(),
        'recipients': 'bbb@bbb.com',
        'type_code': 'EMAIL',
        'status_code': 'FAILURE'
    },
    {
        'id': 3,
        'request_date': datetime.utcnow() - timedelta(hours=AppConfig.DELIVERY_FAILURE_RETRY_TIME_FRAME),
        'recipients': 'cccc@ccc.com',
        'type_code': 'EMAIL',
        'status_code': 'FAILURE'
    },
    {
        'id': 4,
        'request_date': datetime.utcnow() - timedelta(hours=AppConfig.DELIVERY_FAILURE_RETRY_TIME_FRAME + 4),
        'recipients': 'ddd@ddd.com',
        'type_code': 'EMAIL',
        'status_code': 'FAILURE'
    },
    {
        'id': 5,
        'request_date': datetime.utcnow(),
        'recipients': 'eee@eee.com',
        'type_code': 'EMAIL',
        'status_code': 'DELIVERED'
    },
    {
        'id': 6,
        'request_date': datetime.utcnow() - timedelta(hours=AppConfig.DELIVERY_FAILURE_RETRY_TIME_FRAME - 0.5),
        'recipients': 'fff@fff.com',
        'type_code': 'EMAIL',
        'status_code': 'FAILURE'
    },
    {
        'id': 7,
        'request_date': datetime.utcnow() - timedelta(hours=AppConfig.DELIVERY_FAILURE_RETRY_TIME_FRAME, seconds=1),
        'recipients': 'ggg@ggg.com',
        'type_code': 'EMAIL',
        'status_code': 'FAILURE'
    },
    {
        'id': 8,
        'request_date': datetime.utcnow() - timedelta(hours=AppConfig.DELIVERY_FAILURE_RETRY_TIME_FRAME, seconds=-10),
        'recipients': 'hhhh@hhh.com',
        'type_code': 'EMAIL',
        'status_code': 'FAILURE'
    }
]

CONTENT_DATA = [
    {
        'subject': 'test',
        'body': 'test'
    },
    {
        'subject': 'test bytes',
        'body': 'test bytes',
        'attachment_name': 'aaa.txt',
        'attachment': base64.b64decode('dGVzdCB0eHQ=')
    }
]
