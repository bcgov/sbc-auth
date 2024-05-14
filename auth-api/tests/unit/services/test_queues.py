"""ADHOC unit tests for queues."""
import pytest
from dotenv import load_dotenv

from auth_api import create_app
from auth_api.services.activity_log_publisher import Activity, ActivityLogPublisher
from auth_api.utils.account_mailer import publish_to_mailer
from sbc_common_components.utils.enums import QueueMessageTypes


@pytest.mark.skip(reason='ADHOC only test.')
def test_gcp_pubsub_connectivity(monkeypatch):
    """Test that a queue can publish to gcp pubsub."""
    # We don't want any of the monkeypatches by the fixtures.
    monkeypatch.undo()
    load_dotenv('.env')
    app = create_app('production')
    with app.app_context():
        ActivityLogPublisher.publish_activity(Activity(org_id=1, name='hey', action='test'))
        publish_to_mailer(QueueMessageTypes.RESET_PASSCODE.value, {'email': ''})
