from __future__ import annotations
import logging
import base64
from email.message import EmailMessage
from schema import Schema, Literal
from attr import define
from griptape.artifacts import InfoArtifact, ErrorArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient


@define
class GoogleGmailClient(BaseGoogleClient):
    CREATE_DRAFT_EMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
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
                "from",
                description="email address which to send from"
            ): str,
            Literal(
                "body",
                description="body of the email"
            ): str,
            Literal(
                "inbox_owner",
                description="email address of the inbox owner where the draft will be created. if not provided, use the from address"
            ): str
        })
    })
    def create_draft_email(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        values = params["values"]

        try:
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_credentials, scopes=self.CREATE_DRAFT_EMAIL_SCOPES
            )

            delegated_creds = credentials.with_subject(values["inbox_owner"])
            service = build('gmail', 'v1', credentials=delegated_creds)

            message = EmailMessage()
            message.set_content(values["body"])
            message['To'] = values["to"]
            message['From'] = values["from"]
            message['Subject'] = values["subject"]

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
