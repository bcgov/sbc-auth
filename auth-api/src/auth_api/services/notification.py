from flask_mail import Message
from auth_api.extensions import mail


class Notification:

    @staticmethod
    def send_email(subject, sender, recipients, html_body):
        msg = Message(subject, sender=sender, recipients=recipients.split())
        msg.html = html_body
        mail.send(msg)
