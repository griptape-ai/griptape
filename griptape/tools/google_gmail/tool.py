from __future__ import annotations

import base64
import logging
from email.message import EmailMessage

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, InfoArtifact
from griptape.tools import BaseGoogleClient
from griptape.utils.decorators import activity


@define
class GoogleGmailClient(BaseGoogleClient):
    CREATE_DRAFT_EMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

    owner_email: str = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to create a draft email in GMail",
            "schema": Schema(
                {
                    Literal("to", description="email address which to send to"): str,
                    Literal("subject", description="subject of the email"): str,
                    Literal("body", description="body of the email"): str,
                },
            ),
        },
    )
    def create_draft_email(self, params: dict) -> InfoArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(
                scopes=self.CREATE_DRAFT_EMAIL_SCOPES,
                service_name="gmail",
                version="v1",
                owner_email=self.owner_email,
            )

            message = EmailMessage()
            message.set_content(values["body"])
            message["To"] = values["to"]
            message["From"] = self.owner_email
            message["Subject"] = values["subject"]

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"message": {"raw": encoded_message}}
            draft = service.users().drafts().create(userId="me", body=create_message).execute()
            return InfoArtifact(f'An email draft was successfully created (ID: {draft["id"]})')

        except Exception as error:
            logging.error(error)
            return ErrorArtifact(f"error creating draft email: {error}")
