"""
.. module: dispatch.plugins.google_gmail.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from email.mime.text import MIMEText
from typing import Dict, List, Optional
import logging
import smtplib

from tenacity import retry, stop_after_attempt

from dispatch.decorators import apply, counter, timer
from dispatch.messaging.strings import (
    MessageType,
)
from dispatch.plugins.bases import EmailPlugin

from dispatch.messaging.email.utils import create_message_body, create_multi_message_body
from ._version import __version__
from .config import SMTPConfiguration

log = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3))
def send_message(client, message: Dict) -> bool:
    """Sends an email message."""
    try:
        client.sendmail(message["from"], message["to"], message.as_string())
    except smtplib.SMTPException as e:
        log.exception(e)
        return False
    return True


def create_html_message(sender: str, recipient: str, cc: str, subject: str, body: str) -> Dict:
    """Creates a message for an email."""
    message = MIMEText(body, "html")

    message["to"] = recipient
    message["cc"] = cc
    message["from"] = sender
    message["subject"] = subject
    return message


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class SMTPEmailPlugin(EmailPlugin):
    title = "SMTP Email Plugin - Email Management"
    slug = "smtp-email"
    description = "Uses SMTP to facilitate emails."
    version = __version__

    author = "Nvidia"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = SMTPConfiguration

    def send(
        self,
        recipient: str,
        notification_text: str,
        notification_template: dict,
        notification_type: MessageType,
        items: Optional[List] = None,
        **kwargs,
    ):
        """Sends an html email based on the type."""
        # TODO allow for bulk sending (kglisson)

        client = smtplib.SMTP(self.configuration.smtp_server, self.configuration.smtp_port)
        sender = self.configuration.from_email_address
        subject = notification_text

        if kwargs.get("name"):
            subject = f"{kwargs['name'].upper()} - {notification_text}"

        if kwargs.get("subject"):
            subject = kwargs["subject"]

        cc = ""
        if kwargs.get("cc"):
            cc = kwargs["cc"]

        if not items:
            message_body = create_message_body(notification_template, notification_type, **kwargs)
        else:
            message_body = create_multi_message_body(
                notification_template, notification_type, items, **kwargs
            )

        html_message = create_html_message(
            sender,
            recipient,
            cc,
            subject,
            message_body,
        )
        return client.sendmail(sender, recipient, html_message)
