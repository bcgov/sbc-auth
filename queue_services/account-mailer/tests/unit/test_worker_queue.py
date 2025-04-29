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
"""Test Suite to ensure the worker routines are working as expected."""
import os
import types
from datetime import datetime
from unittest.mock import patch

import pytest
from auth_api.services.rest_service import RestService
from google.cloud import storage
from sbc_common_components.utils.enums import QueueMessageTypes

from account_mailer.enums import SubjectType
from account_mailer.services import google_store, notification_service

from . import factory_membership_model, factory_org_model, factory_user_model_with_contact
from .utils import helper_add_event_to_queue


def delete_all_objects(bucket_name):
    """Delete all objects in a bucket."""
    # Set the environment variable for the GCS emulator
    os.environ["CLOUD_STORAGE_EMULATOR_HOST"] = "http://localhost:4443"

    # Initialize the storage client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Delete all objects in the bucket
    for blob in bucket.list_blobs():
        blob.delete()


def create_bucket(bucket_name):
    """Create a bucket in the Fake GCS Server."""
    # Set the environment variable for the GCS emulator
    os.environ["CLOUD_STORAGE_EMULATOR_HOST"] = "http://localhost:4443"

    # Initialize the storage client
    storage_client = storage.Client()

    # Create the bucket
    bucket = storage_client.create_bucket(bucket_name)

    return bucket


def delete_bucket(bucket_name):
    """Delete a bucket from the Fake GCS Server."""
    # Set the environment variable for the GCS emulator
    os.environ["CLOUD_STORAGE_EMULATOR_HOST"] = "http://localhost:4443"

    # Initialize the storage client
    storage_client = storage.Client()
    delete_all_objects(bucket_name)

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    bucket.delete()


def test_refund_request(app, session, client):
    """Assert that the refund request event works."""
    mail_details = {
        "identifier": "NR 123456789",
        "orderNumber": "1",
        "transactionDateTime": "2020-12-12 14:10:20",
        "transactionAmount": 50.00,
        "transactionId": "REG1234",
        "refundDate": "20000101",
        "bcolAccount": "12345",
        "bcolUser": "009900",
    }
    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        helper_add_event_to_queue(
            client,
            QueueMessageTypes.REFUND_DRAWDOWN_REQUEST.value,
            mail_details=mail_details,
        )
        mock_send.assert_called


def test_duplicate_messages(app, session, client):
    """Assert that duplicate messages are handled by the queue.."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id
    mail_details = {"accountId": id, "accountName": org.name}

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.NSF_LOCK_ACCOUNT.value,
            mail_details=mail_details,
            message_id="f76e5ca9-93f3-44ee-a0f8-f47ee83b1971",
        )
        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.NSF_LOCK_ACCOUNT_SUBJECT.value
        assert mock_send.call_args.args[0].get("attachments") is None
        assert True

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.NSF_LOCK_ACCOUNT.value,
            mail_details=mail_details,
            message_id="f76e5ca9-93f3-44ee-a0f8-f47ee83b1971",
        )
        mock_send.assert_not_called


def test_lock_account_mailer_queue(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id
    mail_details = {"accountId": id, "accountName": org.name}
    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.NSF_LOCK_ACCOUNT.value,
            mail_details=mail_details,
        )
        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.NSF_LOCK_ACCOUNT_SUBJECT.value
        assert mock_send.call_args.args[0].get("attachments") is None
        assert True


def test_unlock_account_mailer_queue(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    response = types.SimpleNamespace()
    response.status_code = 200
    response.content = bytes("foo", "utf-8")
    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        with patch.object(RestService, "post", return_value=response):
            # Note: This payload should work with report-api.
            mail_details = {
                "accountId": id,
                "accountName": org.name,
                "invoiceNumber": "REG0123456",
                "receiptNumber": "99123",
                "paymentMethodDescription": "Credit Card",
                "invoice": {
                    "_links": {
                        "self": "http://auth-web.dev.com/api/v1/payment-requests/2",
                        "collection": "http://auth-web.dev.com/api/v1/payment-requests?invoice_id=2",
                    },
                    "bcolAccount": "TEST",
                    "corpTypeCode": "CP",
                    "createdName": "test name",
                    "id": 2,
                    "createdBy": "test",
                    "paymentAccount": {"accountId": "1234", "billable": True},
                    "paymentDate": "2024-02-27T09:52:03+00:00",
                    "total": 130.0,
                    "paymentMethod": "CC",
                    "overdueDate": "2024-03-01T09:52:02+00:00",
                    "paid": 30.0,
                    "details": [{"label": "label", "value": "value"}],
                    "serviceFees": 0.0,
                    "updatedOn": "2024-02-27T09:52:03+00:00",
                    "lineItems": [
                        {
                            "waivedFees": None,
                            "waivedBy": None,
                            "gst": 0.0,
                            "pst": 0.0,
                            "filingFees": 10.0,
                            "id": 2,
                            "serviceFees": 0.0,
                            "priorityFees": 0.0,
                            "futureEffectiveFees": 0.0,
                            "quantity": 1,
                            "statusCode": "ACTIVE",
                            "total": 10.0,
                            "description": "NSF Fee",
                        },
                        {
                            "waivedFees": None,
                            "waivedBy": None,
                            "gst": 0.0,
                            "pst": 0.0,
                            "filingFees": 10.0,
                            "id": 1,
                            "serviceFees": 0.0,
                            "priorityFees": 0.0,
                            "futureEffectiveFees": 0.0,
                            "quantity": 1,
                            "statusCode": "ACTIVE",
                            "total": 10.0,
                            "description": "Name Request",
                        },
                    ],
                    "createdOn": "2024-02-27T09:51:55+00:00",
                    "references": [
                        {
                            "invoiceNumber": "REG00001",
                            "id": 2,
                            "statusCode": "COMPLETED",
                        }
                    ],
                    "receipts": [
                        {
                            "receiptAmount": 100.0,
                            "id": 2,
                            "receiptDate": "2024-02-27T09:52:03.018524",
                            "receiptNumber": "1234567890",
                        }
                    ],
                    "statusCode": "COMPLETED",
                    "folioNumber": "1234567890",
                },
            }
            helper_add_event_to_queue(
                client,
                message_type=QueueMessageTypes.NSF_UNLOCK_ACCOUNT.value,
                mail_details=mail_details,
            )
            mock_send.assert_called
            assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
            assert (
                mock_send.call_args.args[0].get("content").get("subject")
                == SubjectType.NSF_UNLOCK_ACCOUNT_SUBJECT.value
            )
            assert mock_send.call_args.args[0].get("attachments") is None
            assert mock_send.call_args.args[0].get("content").get("body") is not None
            assert True


def test_account_conf_mailer_queue(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        # add an event to queue
        mail_details = {"accountId": id, "nsfFee": "30"}
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.CONFIRMATION_PERIOD_OVER.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.ACCOUNT_CONF_OVER_SUBJECT.value
        assert mock_send.call_args.args[0].get("attachments") is None
        assert mock_send.call_args.args[0].get("content").get("body") is not None


def test_account_pad_invoice_mailer_queue(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        # add an event to queue, these are provided by cfs_create_invoice_task.
        mail_details = {
            "accountId": id,
            "credit_total": "20",
            "nsfFee": "30",
            "invoice_total": "100",
            "invoice_process_date": f"{datetime.now()}",
            "withdraw_total": "80",
            "invoice_number": "1234567890",
        }
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.PAD_INVOICE_CREATED.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.PAD_INVOICE_CREATED.value
        assert mock_send.call_args.args[0].get("attachments") is None

        email_body = mock_send.call_args.args[0].get("content").get("body")
        assert email_body is not None
        assert "This email confirms recent transaction(s) on your account" in email_body
        assert "Invoice reference number: 1234567890" in email_body
        assert "Transaction date:" in email_body
        assert "Log in to view transaction details" in email_body
        assert "/account/{org_id}/settings/transactions".format(org_id=org.id) in email_body


def test_account_admin_removed(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        email = "foo@testbar.com"
        mail_details = {"accountId": id, "recipientEmail": email}
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.ADMIN_REMOVED.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == email
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.ADMIN_REMOVED_SUBJECT.value
        assert mock_send.call_args.args[0].get("attachments") is None
        assert mock_send.call_args.args[0].get("content").get("body") is not None


def test_account_team_modified(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        mail_details = {
            "accountId": id,
        }
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.TEAM_MEMBER_INVITED.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.TEAM_MODIFIED_SUBJECT.value
        assert mock_send.call_args.args[0].get("attachments") is None
        assert mock_send.call_args.args[0].get("content").get("body") is not None


def test_online_banking_emails(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        mail_details = {"amount": "100.00", "creditAmount": "10.00", "accountId": id}
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.ONLINE_BANKING_UNDER_PAYMENT.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert (
            mock_send.call_args.args[0].get("content").get("subject")
            == SubjectType.ONLINE_BANKING_PAYMENT_SUBJECT.value
        )
        assert mock_send.call_args.args[0].get("attachments") is None
        assert mock_send.call_args.args[0].get("content").get("body") is not None

        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.ONLINE_BANKING_OVER_PAYMENT.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert (
            mock_send.call_args.args[0].get("content").get("subject")
            == SubjectType.ONLINE_BANKING_PAYMENT_SUBJECT.value
        )
        assert mock_send.call_args.args[0].get("attachments") is None
        assert mock_send.call_args.args[0].get("content").get("body") is not None

        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.ONLINE_BANKING_PAYMENT.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert (
            mock_send.call_args.args[0].get("content").get("subject")
            == SubjectType.ONLINE_BANKING_PAYMENT_SUBJECT.value
        )
        assert mock_send.call_args.args[0].get("attachments") is None
        assert mock_send.call_args.args[0].get("content").get("body") is not None


def test_pad_failed_emails(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        mail_details = {"accountId": id}
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.PAD_SETUP_FAILED.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.PAD_SETUP_FAILED.value
        assert mock_send.call_args.args[0].get("attachments") is None
        assert mock_send.call_args.args[0].get("content").get("body") is not None

        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.PAD_SETUP_FAILED.value,
            mail_details=mail_details,
        )


def test_payment_pending_emails(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        mail_details = {
            "accountId": id,
            "cfsAccountId": "12345678",
            "transactionAmount": 20.00,
        }
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.PAYMENT_PENDING.value,
            mail_details=mail_details,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "foo@bar.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.PAYMENT_PENDING.value
        assert mock_send.call_args.args[0].get("attachments") is None
        assert mock_send.call_args.args[0].get("content").get("body") is not None

        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.PAYMENT_PENDING.value,
            mail_details=mail_details,
        )


@pytest.mark.skip(reason="Skipping until pay queue switches to google storage")
def test_ejv_failure_emails(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    gcs_file_name = "FEEDBACK.1234567890"
    gcs_bucket = "cgi-ejv"
    try:
        with patch.object(notification_service, "send_email", return_value=None) as mock_send:

            # Set the environment variable for the GCS emulator
            os.environ["CLOUD_STORAGE_EMULATOR_HOST"] = "http://localhost:4443"
            os.environ["STORAGE_EMULATOR_HOST"] = "http://localhost:4443"  # Add this if needed

            # Create the bucket in the GCS emulator
            create_bucket(gcs_bucket)
            # Create a temporary file for testing
            with open(gcs_file_name, "w") as jv_file:
                jv_file.write("TEST")
            # Upload the file to the GCS emulator
            google_store.GoogleStoreService.upload_file_to_bucket(gcs_bucket, gcs_file_name, gcs_file_name)

            file_content = google_store.GoogleStoreService.download_file_from_bucket(gcs_bucket, gcs_file_name)
            assert file_content == b"TEST", f"File content mismatch: {file_content}"

            # Add an event to the queue
            mail_details = {
                "fileName": gcs_file_name,
                "minioLocation": gcs_bucket,  # TODO change this value later
            }

            # Ensure Pub/Sub emulator is correctly set up
            helper_add_event_to_queue(
                client,
                message_type=QueueMessageTypes.EJV_FAILED.value,
                mail_details=mail_details,
            )

            # Verify the email was sent
            mock_send.assert_called()
            assert mock_send.call_args.args[0].get("recipients") == "test@test.com"
            assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.EJV_FAILED.value
    finally:
        delete_bucket(gcs_bucket)


def test_passcode_reset_email(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        msg_payload = {
            "emailAddresses": "test@test.com",
            "passCode": "1234",
            "businessIdentifier": "CP1234",
            "businessName": "TEST",
            "isStaffInitiated": True,
        }
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.RESET_PASSCODE.value,
            mail_details=msg_payload,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "test@test.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.RESET_PASSCODE.value

        # add an event to queue - staff initiated reset
        msg_payload = {
            "emailAddresses": "test@test.com",
            "passCode": "1234",
            "businessIdentifier": "CP1234",
            "businessName": "TEST",
            "isStaffInitiated": False,
        }
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.RESET_PASSCODE.value,
            mail_details=msg_payload,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "test@test.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.RESET_PASSCODE.value


def test_statement_notification_email(app, session, client):
    """Assert that statement notification events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        msg_payload = {
            "accountId": id,
            "fromDate": "2023-09-15 00:00:00",
            "toDate": "2023-10-15 00:00:00",
            "emailAddresses": "test@test.com",
            "statementFrequency": "MONTHLY",
            "totalAmountOwing": 351.5,
        }
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.STATEMENT_NOTIFICATION.value,
            mail_details=msg_payload,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "test@test.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.STATEMENT_NOTIFICATION.value


def test_payment_reminder_notification_email(app, session, client):
    """Assert that payment reminder notification events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id

    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        msg_payload = {
            "accountId": id,
            "dueDate": "2023-09-15 00:00:00",
            "emailAddresses": "test@test.com",
            "statementFrequency": "MONTHLY",
            "statementMonth": "August",
            "statementNumber": 12345,
            "totalAmountOwing": 351.5,
            "shortNameLinksCount": 1,
        }
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.PAYMENT_REMINDER_NOTIFICATION.value,
            mail_details=msg_payload,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "test@test.com"
        assert (
            mock_send.call_args.args[0].get("content").get("subject") == SubjectType.PAYMENT_REMINDER_NOTIFICATION.value
        )


def test_payment_due_notification_email(app, session, client):
    """Assert that payment due notification events can be retrieved and decoded from the Queue."""
    user = factory_user_model_with_contact()
    org = factory_org_model()
    factory_membership_model(user.id, org.id)
    id = org.id
    with patch.object(notification_service, "send_email", return_value=None) as mock_send:
        msg_payload = {
            "accountId": id,
            "dueDate": "2023-09-15 00:00:00",
            "emailAddresses": "test@test.com",
            "statementFrequency": "MONTHLY",
            "statementMonth": "August",
            "statementNumber": 12345,
            "totalAmountOwing": 351.5,
            "shortNameLinksCount": 1,
        }
        helper_add_event_to_queue(
            client,
            message_type=QueueMessageTypes.PAYMENT_DUE_NOTIFICATION.value,
            mail_details=msg_payload,
        )

        mock_send.assert_called
        assert mock_send.call_args.args[0].get("recipients") == "test@test.com"
        assert mock_send.call_args.args[0].get("content").get("subject") == SubjectType.PAYMENT_DUE_NOTIFICATION.value
