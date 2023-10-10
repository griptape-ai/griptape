from __future__ import annotations
import logging
import base64
from email.message import EmailMessage
from schema import Schema, Literal, Optional
from attr import define, field
from griptape.artifacts import InfoArtifact, ErrorArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient


@define
class GoogleGmailClient(BaseGoogleClient):
    CREATE_DRAFT_EMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

    owner_email: str = field(kw_only=True)

    @activity(config={
        "description": "Can be used to create a draft email in GMail",
        "schema": Schema({
            Literal(
                "to",
                description="email address which to send to"
            ): str,
            Literal(
                "subject",
                description="subject of the email"
            ): str,
            Literal(
                "body",
                description="body of the email"
            ): str,
            Optional(Literal(
                "attachments",
                description="List of file paths to be attached to the email"
            )): list[str],
        })
    })
    def create_draft_email(self, params: dict) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        to_address = values.get("to")
        subject = values.get("subject")
        body = values.get("body")
        attachments = values.get("attachments", [])

        try:
            service = self._build_client(
                scopes=self.CREATE_DRAFT_EMAIL_SCOPES,
                service_name='gmail',
                version='v1',
                owner_email=self.owner_email
            )

            message = EmailMessage()
            message.set_content(body)
            message['To'] = to_address
            message['From'] = self.owner_email
            message['Subject'] = subject

            for attachment in attachments:
                with open(attachment, "rb") as f:
                    file_data = f.read()
                    file_name = attachment.split("/")[-1]
                    message.add_attachment(file_data, maintype='application',
                                           subtype='octet-stream', filename=file_name)

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {
                'message': {
                    'raw': encoded_message
                }
            }
            draft = service.users().drafts().create(userId='me', body=create_message).execute()
            return InfoArtifact(f'An email draft was successfully created (ID: {draft["id"]})')

        except Exception as error:
            logging.error(error)
            return ErrorArtifact(f'error creating draft email: {error}')
