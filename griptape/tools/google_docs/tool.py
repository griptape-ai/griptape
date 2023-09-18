from __future__ import annotations
import logging
from attr import field, define
from schema import Schema, Literal, Or
from attr import define
from griptape.artifacts import ErrorArtifact, InfoArtifact, BlobArtifact, ListArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient
from googleapiclient.discovery import Resource


@define
class GoogleDocsClient(BaseGoogleClient):
    owner_email: str = field(default=None)
    DOCS_SCOPES = ['https://www.googleapis.com/auth/documents']
    DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def _build_client(self, scopes: list[str], version: str, tool: str) -> Resource:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(self.owner_email)
        service = build(tool, version, credentials=delegated_credentials)
        return service

    def create_google_doc(self, file_name: str) -> InfoArtifact | ErrorArtifact:
        try:
            service = self._build_client(self.DOCS_SCOPES, "v1", "docs")
            doc = service.documents().create(body={"title": file_name}).execute()
            return InfoArtifact(f"Google Doc '{file_name}' created with ID: {doc['documentId']}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error creating Google Doc: {e}")

    def append_text(self, params: dict, text: str) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        try:
            service = self._build_client(self.DOCS_SCOPES, "v1", "docs")
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
            service = self._build_client(self.DOCS_SCOPES, "v1", "docs")
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
            service = self._build_client(self.DRIVE_SCOPES, "v3", "drive")
            file_metadata = {
                'name': values['file_name'],
                'mimeType': 'application/vnd.google-apps.document'
            }
            media = MediaFileUpload(values['file_path'], mimetype=values['mime_type'])
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return InfoArtifact(f'A document was successfully uploaded with ID {file.get("id")}.')
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error uploading document to Google Docs: {e}")

    def get_file_id_from_path(self, path: str) -> str | None:
        parts = path.split('/')
        current_parent_id = 'root'
        service = self._build_client(self.DRIVE_SCOPES, "v3", "drive")
        for part in parts:
            response = service.files().list(q=f"'{current_parent_id}' in parents and name='{part}' and trashed=false",
                                            spaces='drive',
                                            fields='files(id, name)').execute()
            if not response.get('files'):
                return None
            current_parent_id = response['files'][0]['id']
        return current_parent_id

    def download_document(self, file_path: str) -> BlobArtifact | ErrorArtifact:
        try:
            service = self._build_client(self.DRIVE_SCOPES, "v3", "drive")
            results = service.files().list(q=f"name='{file_path}'", spaces='drive', pageSize=10).execute()
            items = results.get('files', [])
            if not items:
                return ErrorArtifact(f"Error: File not found for path {file_path}")
            file_id = items[0]['id']
            request = service.files().export(fileId=file_id, mimeType='text/plain')
            response = request.execute()

            return BlobArtifact(response)

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error downloading Google Doc: {e}")

    @activity(config={
        "description": "Can be used to load Google Docs based on their paths",
        "schema": Schema({
            Literal(
                "file_paths",
                description="Paths to the Google Docs to be loaded. For example, ['folder_name/document_name']"
            ): [Or(str)]
        })
    })
    def load_docs_from_drive(self, file_paths: list[str]) -> ListArtifact | ErrorArtifact:
        downloaded_files = []

        for path in file_paths:
            blob = self.download_document(path)
            if isinstance(blob, ErrorArtifact):
                return ErrorArtifact(f"Error downloading Google Doc for path {path}: {blob.value}")
            downloaded_files.append(blob)

        return ListArtifact(downloaded_files)

