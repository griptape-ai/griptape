from __future__ import annotations
import logging
from schema import Schema, Literal, Optional
from attr import define
from griptape.artifacts import ErrorArtifact, InfoArtifact, TextArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient
from googleapiclient.errors import HttpError
from google.auth.exceptions import MalformedError


@define
class GoogleDocsClient(BaseGoogleClient):
    DOCS_SCOPES = ['https://www.googleapis.com/auth/documents']
    DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']

    @activity(config={
        "description": "Can be used to interact with Google Docs",
        "schema": Schema({
            Literal(
                "drive_owner_email",
                description="email of the Google Drive's owner"
            ): str,
        })
    })
    def _build_client(self, scopes: list[str], values: dict) -> object:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(values["drive_owner_email"])
        service = build('docs', 'v1', credentials=delegated_credentials)
        return service

    def create_google_doc(self, params: dict, file_name: str) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        try:
            service = self._build_client(self.DOCS_SCOPES, values)

            doc = service.documents().create(body={"title": file_name}).execute()

            return InfoArtifact(f"Google Doc '{file_name}' created with ID: {doc['documentId']}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error creating Google Doc: {e}")

    def append_text(self, params: dict, text: str) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        try:
            service = self._build_client(self.DOCS_SCOPES, values)
            doc = service.documents().get(documentId=values["document_id"]).execute()
            end_index = doc['body']['content'][-1]['endIndex']
            requests = [
                {'insertText': {
                    'location': {'index': end_index},
                    'text': text
                }}
            ]
            doc = service.documents().batchUpdate(documentId=values["document_id"], body={'requests': requests}).execute()
            return InfoArtifact("Text appended successfully")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error appending text to Google Doc: {e}")

    def prepend_text(self, params: dict, text: str) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        try:
            service = self._build_client(self.DOCS_SCOPES, values)
            requests = [
                {'insertText': {
                    'location': {'index': 0},
                    'text': text
                }}
            ]
            doc = service.documents().batchUpdate(documentId=values["document_id"], body={'requests': requests}).execute()
            return InfoArtifact("Text prepended successfully")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error prepending text to Google Doc: {e}")

    @activity(config={
        "description": "Can be used to upload a document to Google Docs",
        "schema": Schema({
            Literal(
                "drive_owner_email",
                description="email of the Google Drive's owner"
            ): str,
            Literal(
                "file_path",
                description="path to the file to be uploaded"
            ): str,
            Literal(
                "file_name",
                description="name to give the document on Google Docs"
            ): str,
            Literal(
                "mime_type",
                description="MIME type of the document being uploaded"
            ): str
        })
    })
    def upload_document(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.discovery import build
        from google.oauth2 import service_account

        values = params['values']

        try:
            # Build the drive service as you're uploading to Google Drive
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_credentials, scopes=self.DRIVE_SCOPES
            )
            delegated_credentials = credentials.with_subject(values["drive_owner_email"])
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

            file_metadata = {'name': values['file_name']}
            media = MediaFileUpload(values['file_path'], mimetype=values['mime_type'])
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            return InfoArtifact(f'A document was successfully uploaded with ID {file.get("id")}.')

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error uploading document to Google Docs: {e}")

    @activity(config={
        "description": "Can be used to download a document from Google Docs",
        "schema": Schema({
            Literal(
                "drive_owner_email",
                description="email of the Google Drive's owner"
            ): str,
            Literal(
                "file_id",
                description="ID of the document to be downloaded from Google Docs"
            ): str
        })
    })
    def download_document(self, params: dict) -> TextArtifact | ErrorArtifact:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account

        values = params["values"]

        try:
            # Build the drive service as you're downloading from Google Drive
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_credentials, scopes=self.DRIVE_SCOPES
            )
            delegated_credentials = credentials.with_subject(values["drive_owner_email"])
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

            request = drive_service.files().get_media(fileId=values["file_id"])
            downloaded_file = request.execute()

            return TextArtifact(downloaded_file)

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"error downloading document from Google Docs: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error downloading document due to malformed credentials")
