from __future__ import annotations
import imaplib
import json
import logging
import smtplib
from email.mime.text import MIMEText
from typing import Optional
import schema
from attr import define, field
from griptape.artifacts import ErrorArtifact, InfoArtifact, TextArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Literal


@define
class EmailClient(BaseTool):
    """
    Attributes:
        username: Used by default for both SMTP and IMAP activities. Will be used as the from email when sending emails.
        password: Used by default for both SMTP and IMAP activities.
        email_max_retrieve_count: Used to limit the number of messages retrieved during any given activities.
        smtp_host: The hostname or url of the SMTP server (smtp.gmail.com).
        smtp_port: The port name of the SMTP server (465).
        smtp_use_ssl: Should EmailClient use SSL when sending.
        smtp_user: Setting this will override whatever is set as the username parameter for SMTP activities.
        smtp_password: Setting this will override whatever is set as the username parameter for SMTP activities.
        imap_url: The hostname or url of the SMTP server (imap.gmail.com).
        imap_user: Setting this will override whatever is set as the username parameter for IMAP activities.
        imap_password: Setting this will override whatever is set as the username parameter for IMAP activities.
    """
    # if you set imap|smtp creds explicitly these fields will be overridden
    username: Optional[str] = field(default=None, kw_only=True)
    password: Optional[str] = field(default=None, kw_only=True)

    smtp_host: Optional[str] = field(default=None, kw_only=True)
    smtp_port: Optional[int] = field(default=None, kw_only=True)
    smtp_use_ssl: bool = field(default=True, kw_only=True)

    # if you set the smtp user/password fields they will override
    smtp_user: Optional[str] = field(default=None, kw_only=True)
    smtp_password: Optional[str] = field(default=None, kw_only=True)

    imap_url: Optional[str] = field(default=None, kw_only=True)

    # if you set imap user/password fields they will override
    imap_user: Optional[str] = field(default=None, kw_only=True)
    imap_password: Optional[str] = field(default=None, kw_only=True)

    email_max_retrieve_count: Optional[int] = field(default=None, kw_only=True)

    mailboxes: Optional[dict[str, str]] = field(default=None, kw_only=True)

    @activity(config={
        "description": "Can be used to retrieve emails."
                       "{% if _self.mailboxes %} Available mailboxes: {{ _self.mailboxes }}{% endif %}",
        "schema": Schema({
            Literal(
                "label",
                description="Label to retrieve emails from such as 'INBOX' or 'SENT'"
            ): str,
            schema.Optional(
                Literal(
                    "key",
                    description="Optional key for filtering such as 'FROM' or 'SUBJECT'"
                )
            ): str,
            schema.Optional(
                Literal(
                    "search_criteria",
                    description="Optional search criteria to filter emails by key"
                )
            ): str,
            schema.Optional(
                Literal(
                    "max_count",
                    description="Optional max email count"
                )
            ): int
        })
    })
    def retrieve(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]
        imap_user = self.imap_user if self.imap_user else self.username
        imap_password = self.imap_password if self.imap_password else self.password
        max_count = int(values["max_count"]) if values.get("max_count") else self.email_max_retrieve_count
        list_artifact = ListArtifact()

        try:
            import mailparser

            con = imaplib.IMAP4_SSL(self.imap_url)

            con.login(imap_user, imap_password)

            mailbox = con.select(f'"{values["label"]}"', readonly=True)

            if mailbox[0] == "OK":
                if values.get("key") and values.get("search_criteria"):
                    messages_count = len(
                        con.search(
                            None, values["key"], f'"{values["search_criteria"]}"'
                            )[1][0].decode().split(" ")
                    )
                else:
                    messages_count = int(mailbox[1][0])

                top_n = max(0, messages_count - max_count) if max_count else 0

                for i in range(messages_count, top_n, -1):
                    result, data = con.fetch(str(i), "(RFC822)")
                    message = mailparser.parse_from_bytes(data[0][1])

                    list_artifact.value.append(
                        TextArtifact("\n".join(message.text_plain))
                    )

                con.close()
                con.logout()

                return list_artifact
            else:
                return ErrorArtifact(mailbox[1][0].decode())
        except Exception as e:
            logging.error(e)

            return ErrorArtifact(f"error retrieving email {e}")

    @activity(config={
        "description": "Can be used to send emails",
        "schema": Schema({
            Literal(
                "to",
                description="Recipient's email address"
            ): str,
            Literal(
                "subject",
                description="Email subject"
            ): str,
            Literal(
                "body",
                description="Email body"
            ): str
        })
    })
    def send(self, params: dict) -> InfoArtifact | ErrorArtifact:
        input_values = params["values"]
        server: Optional[smtplib.SMTP] = None

        # email username can be overridden by setting the smtp user explicitly
        smtp_user = self.smtp_user
        if smtp_user is None:
            smtp_user = self.username

        # email password can be overridden by setting the smtp password explicitly
        smtp_password = self.smtp_password
        if smtp_password is None:
            smtp_password = self.password

        smtp_host = self.smtp_host
        smtp_port = int(self.smtp_port)

        to_email = input_values["to"]
        subject = input_values["subject"]
        msg = MIMEText(input_values["body"])

        try:
            if self.smtp_use_ssl:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)

            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = to_email

            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())

            return InfoArtifact("email was successfully sent")
        except Exception as e:
            logging.error(e)

            return ErrorArtifact(f"error sending email: {e}")
        finally:
            try:
                server.quit()
            except Exception as e:
                logging.error(e)
