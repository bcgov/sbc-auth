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
"""Service for managing Invitation data."""


from flask_mail import Message

from notify_api.extensions import mail


class Notify:  # pylint: disable=too-few-public-methods
    """Class that manages notify."""

    @staticmethod
    def send_email(subject, sender, recipients, html_body):
        """Send the email using the given details."""
        msg = Message(subject, sender=sender, recipients=recipients.split())
        msg.html = html_body
        mail.send(msg)
