from datetime import datetime, timedelta

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
        'request_date': datetime.utcnow() - timedelta(hours=1),
        'recipients': 'bbb@bbb.com',
        'type_code': 'EMAIL',
        'status_code': 'FAILURE'
    },
    {
        'id': 4,
        'request_date': datetime.utcnow() - timedelta(hours=5),
        'recipients': 'ccc@ccc.com',
        'type_code': 'EMAIL',
        'status_code': 'FAILURE'
    },
    {
        'id': 5,
        'request_date': datetime.utcnow(),
        'recipients': 'ddd@ddd.com',
        'type_code': 'EMAIL',
        'status_code': 'DELIVERED'
    }
]

NOTIFICATION_REQUEST_DATA = [
    {
        'recipients': 'aaa@aaa.com',
        'contents': {
            'subject': 'test url',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa@aaa.com, bbb@aaa.com',
        'contents': {
            'subject': 'test url',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    }
]


NOTIFICATION_REQUEST_BAD_DATA = [
    {
        'recipients': '',
        'contents': {
            'subject': 'test url',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'contents': {
            'subject': 'test url',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa',
        'contents': {
            'subject': 'test url',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa@aaa.com, bbbb',
        'contents': {
            'subject': 'test url',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa@aaa.com, bbbb@bbb',
        'contents': {
            'subject': 'test url',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa.com, bbbb@bbb.com',
        'contents': {
            'subject': 'test url',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa@aaa.com',
        'contents': {
            'subject': '',
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa@aaa.com',
        'contents': {
            'body': 'test url',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa@aaa.com',
        'contents': {
            'subject': 'aa',
            'body': '',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    },
    {
        'recipients': 'aaa@aaa.com',
        'contents': {
            'subject': 'aaa',
            'attachmentName': 'aaa.pdf',
            'attachmentBytes': '',
            'attachmentUrl': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
        }
    }
]

CONTENT_DATA = [
    {
        'id': 1,
        'subject': 'test',
        'body': 'test'
    },
    {
        'id': 2,
        'subject': 'test pdf',
        'body': 'test pdf',
        'attachment_name': 'aaa.pdf',
        'attachment': '',
        'attachment_url': 'https://www.antennahouse.com/XSLsample/pdf/sample-link_1.pdf'
    },
    {
        'id': 3,
        'subject': 'test bytes',
        'body': 'test bytes',
        'attachment_name': 'aaa.txt',
        'attachment': 'dGVzdCB0eHQ=',
        'attachment_url': ''
    }
]
