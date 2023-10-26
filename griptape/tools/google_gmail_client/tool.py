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
                    Optional("attachments", description="Optional list of attachments loaded from memory"): [
                        {"attachment_name": str, "memory_name": str, "artifact_namespace": str}
                    ],
                }
            ),
        }
    )
    def create_draft_email(self, params: dict) -> InfoArtifact | ErrorArtifact:
        values = params["values"]

        message = self._create_email_message(values)
        if values.get("attachments"):
            self._attach_files_to_message(message, values)

        try:
            service = self._build_client(
                scopes=self.CREATE_DRAFT_EMAIL_SCOPES, service_name="gmail", version="v1", owner_email=self.owner_email
            )
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"message": {"raw": encoded_message}}
            draft = service.users().drafts().create(userId="me", body=create_message).execute()
            return InfoArtifact(f'An email draft was successfully created (ID: {draft["id"]})')

        except Exception as error:
            logging.error(error)
            return ErrorArtifact(f"error creating draft email: {error}")

    def _create_email_message(self, values: dict) -> EmailMessage:
        to_address = values.get("to")
        subject = values.get("subject")
        body = values.get("body")

        message = EmailMessage()
        message.set_content(body)
        message["To"] = to_address
        message["From"] = self.owner_email
        message["Subject"] = subject

        return message

    def _attach_files_to_message(self, message: EmailMessage, values: dict) -> None:
        attachments = values.get("attachments")

        for index, attachment in enumerate(attachments):
            memory_name = attachment.get("memory_name")
            artifact_namespace = attachment.get("artifact_namespace")
            attachment_name = attachment.get("attachment_name")

            memory = self.find_input_memory(memory_name)

            if memory:
                list_artifact = memory.load_artifacts(artifact_namespace)

                if list_artifact:
                    # Using order-based logic to fetch the right artifact
                    if len(list_artifact.value) > index:
                        file_data = list_artifact.value[index].value.encode()
                        message.add_attachment(
                            file_data, maintype="application", subtype="octet-stream", filename=attachment_name
                        )
                    else:
                        logging.error(f"Artifact index {index} out of bounds for namespace {artifact_namespace}.")
                else:
                    logging.error(f"Artifact with namespace {artifact_namespace} not found.")
            else:
                logging.error("memory not found.")
