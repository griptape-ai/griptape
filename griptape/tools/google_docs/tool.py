from __future__ import annotations
import logging
from attr import field, define
from schema import Schema, Literal, Or, Optional
from griptape.artifacts import ErrorArtifact, InfoArtifact, BlobArtifact, ListArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient
from googleapiclient.discovery import Resource


@define
class GoogleDocsClient(BaseGoogleClient):
    DOCS_SCOPES = ['https://www.googleapis.com/auth/documents']

    DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']

    owner_email: str = field(default=None)

    @activity(config={
        "description": "Create a new Google Doc in Drive",
        "schema": Schema({
            "file_path": Or(str)
        })
    })
    def create_google_doc(self, file_path: str) -> InfoArtifact | ErrorArtifact:
        try:
            file_name = file_path.split("/")[-1]
            service = self._build_client(self.DOCS_SCOPES, "v1", "docs")
            doc = service.documents().create(body={"title": file_name}).execute()
            return InfoArtifact(f"Google Doc '{file_name}' created with ID: {doc['documentId']}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error creating Google Doc: {e}")

    @activity(config={
        "description": "Append text to a Google Doc",
        "schema": Schema({
            "file_path": Or(str),
            "text": Or(str)
        })
    })
    def append_text(self, file_path: str, text: str) -> InfoArtifact | ErrorArtifact:
        try:
            service = self._build_client(self.DOCS_SCOPES, "v1", "docs")
            drive_service = self._build_client(self.DRIVE_SCOPES, "v3", "drive")
            document_id = self._path_to_file_id(drive_service, file_path)
            if document_id:
                doc = service.documents().get(documentId=document_id).execute()
                content = doc["body"]["content"]
                last_text = content[-1]["paragraph"]["elements"][-1]["textRun"]["content"]
                append_index = content[-1]["endIndex"]
                if last_text.endswith("\n"):
                    append_index -= 1
                
                requests = [{"insertText": {"location": {"index": append_index}, "text": text}}]
                
                doc = service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
                return InfoArtifact("Text appended successfully")
            else:
                return ErrorArtifact(f"Error: File not found for path {file_path}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error appending text to Google Doc: {e}")

    @activity(config={
        "description": "Prepend text to a Google Doc",
        "schema": Schema({
            "file_path": Or(str),
            "text": Or(str)
        })
    })
    def prepend_text(self, file_path: str, text: str) -> InfoArtifact | ErrorArtifact:
        try:
            service = self._build_client(self.DOCS_SCOPES, "v1", "docs")
            drive_service = self._build_client(self.DRIVE_SCOPES, "v3", "drive")
            document_id = self._path_to_file_id(drive_service, file_path)
            if document_id:
                doc = service.documents().get(documentId=document_id).execute()
                
                if len(doc["body"]["content"]) == 1:
                    requests = [{"insertText": {"location": {"index": 1}, "text": text}}]
                else:
                    start_index = doc["body"]["content"][1]["startIndex"]
                    requests = [{"insertText": {"location": {"index": start_index}, "text": text}}]
                
                doc = service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
                return InfoArtifact("Text prepended successfully")
            else:
                return ErrorArtifact(f"Error: File not found for path {file_path}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error prepending text to Google Doc: {e}")

    @activity(
        config={
            "description": "Can be used to Download multiple Google Docs from Google Drive based on their paths",
            "schema": Schema({"file_paths": [Or(str)]}),
        }
    )
    def load_docs_from_drive(self, file_paths: list[str]) -> ListArtifact | ErrorArtifact:
        downloaded_files = []
    
        for path in file_paths:
            blob = self.download_document(path)
            if isinstance(blob, ErrorArtifact):
                return ErrorArtifact(f"Error downloading Google Doc for path {path}: {blob.value}")
            downloaded_files.append(blob)
    
        return ListArtifact(downloaded_files)

    def _download_document(self, file_path: str) -> BlobArtifact | ErrorArtifact:
        try:
            service = self._build_client(self.DRIVE_SCOPES, "v3", "drive")
            file_id = self._path_to_file_id(service, file_path)
            if file_id:
                results = service.files().list(q=f"name='{file_path}'", spaces='drive', pageSize=10).execute()
                items = results.get('files', [])
                if not items:
                    return ErrorArtifact(f"Error: File not found for path {file_path}")
                file_id = items[0]['id']
                request = service.files().export(fileId=file_id, mimeType='text/plain')
                response = request.execute()

                return BlobArtifact(response)
            else:
                return ErrorArtifact(f"Error: File not found for path {file_path}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error downloading Google Doc: {e}")

    def _build_client(self, scopes: list[str], version: str, tool: str) -> Resource:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(self.owner_email)
        service = build(tool, version, credentials=delegated_credentials)
        return service

    def _path_to_file_id(self, service, path: str) -> Optional[str]:
        parts = path.split("/")
        current_id = "root"
    
        for idx, part in enumerate(parts):
            if idx == len(parts) - 1:
                query = f"name='{part}' and '{current_id}' in parents"
            else:
                query = f"name='{part}' and '{current_id}' in parents and mimeType='application/vnd.google-apps.folder'"
    
            response = service.files().list(q=query).execute()
            files = response.get("files", [])
    
            if not files and idx != len(parts) - 1:
                folder_metadata = {"name": part, "mimeType": "application/vnd.google-apps.folder", "parents": [current_id]}
                folder = service.files().create(body=folder_metadata, fields="id").execute()
                current_id = folder.get("id")
            elif files:
                current_id = files[0]["id"]
            else:
                return None
    
        return current_id
