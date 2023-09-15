from __future__ import annotations
import logging
from schema import Schema, Literal
from attr import define
from griptape.artifacts import ErrorArtifact, InfoArtifact, BlobArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient
from googleapiclient.errors import HttpError
from google.auth.exceptions import MalformedError
from googleapiclient.discovery import Resource


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
    def _build_client(self, scopes: list[str], values: dict, version: str, tool: str) -> Resource:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(values["drive_owner_email"])
        service = build(tool, version, credentials=delegated_credentials)
        return service

    def create_google_doc(self, params: dict, file_name: str) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        try:
            service = self._build_client(self.DOCS_SCOPES, values, "v1", "docs")

            doc = service.documents().create(body={"title": file_name}).execute()

            return InfoArtifact(f"Google Doc '{file_name}' created with ID: {doc['documentId']}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error creating Google Doc: {e}")

    def append_text(self, params: dict, text: str) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        try:
            service = self._build_client(self.DOCS_SCOPES, values, "v1", "docs")
            doc = service.documents().get(documentId=values["document_id"]).execute()
            content = doc['body']['content']
            last_text = content[-1]['paragraph']['elements'][-1]['textRun']['content']
            append_index = content[-1]['endIndex']
            if last_text.endswith("\n"):
                append_index -= 1

            print("Appending at index:", append_index)

            requests = [
                {'insertText': {
                    'location': {'index': append_index},
                    'text': text
                }}
            ]

            doc = service.documents().batchUpdate(documentId=values["document_id"],
                                                  body={'requests': requests}).execute()
            return InfoArtifact("Text appended successfully")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error appending text to Google Doc: {e}")

    def prepend_text(self, params: dict, text: str) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        try:
            service = self._build_client(self.DOCS_SCOPES, values, "v1", "docs")
            doc = service.documents().get(documentId=values["document_id"]).execute()
            if len(doc['body']['content']) == 1:
                requests = [
                    {'insertText': {
                        'location': {'index': 1},
                        'text': text
                    }}
                ]
            else:
                start_index = doc['body']['content'][1]['startIndex']
                requests = [
                    {'insertText': {
                        'location': {'index': start_index},
                        'text': text
                    }}
                ]

            doc = service.documents().batchUpdate(documentId=values["document_id"],
                                                  body={'requests': requests}).execute()
            return InfoArtifact("Text prepended successfully")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error prepending text to Google Doc: {e}")

    def upload_document(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.http import MediaFileUpload

        values = params['values']

        try:
            service = self._build_client(self.DRIVE_SCOPES, values, "v3", "drive")
            file_metadata = {'name': values['file_name']}
            media = MediaFileUpload(values['file_path'], mimetype=values['mime_type'])
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return InfoArtifact(f'A document was successfully uploaded with ID {file.get("id")}.')

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error uploading document to Google Docs: {e}")

    def download_document(self, params: dict) -> BlobArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(self.DRIVE_SCOPES, values, "v3", "drive")
            request = service.files().get_media(fileId=values["file_id"])
            downloaded_file = request.execute()
            return BlobArtifact(downloaded_file)

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"error downloading document from Google Docs: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error downloading document due to malformed credentials")
