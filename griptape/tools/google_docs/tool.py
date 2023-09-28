from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from attr import field, define
from schema import Schema, Optional, Literal
from griptape.artifacts import ErrorArtifact, InfoArtifact, BlobArtifact, ListArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource

@define
class GoogleDocsClient(BaseGoogleClient):
    DOCS_SCOPES = ["https://www.googleapis.com/auth/documents"]

    DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    owner_email: str = field(default=None)

    @activity(
        config={
            "description": "Can be used to create a new Google Doc in Drive",
            "schema": Schema(
                {
                    Literal(
                        "file_name",
                        description="Name of the file to be created."
                    ): str
                }
            ),
        }
    )
    def create_google_doc(self, params: dict) -> InfoArtifact | ErrorArtifact:
        try:
            file_name = params["file_name"]
            service = self._build_client(self.DOCS_SCOPES, "v1", "docs")
            doc = service.documents().create(body={"title": file_name}).execute()
            return InfoArtifact(f"Google Doc '{file_name}' created with ID: {doc['documentId']}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error creating Google Doc: {e}")

    @activity(
        config={
            "description": "Can be used to append text to a Google Doc",
            "schema": Schema(
                {
                    Literal(
                        "file_path",
                        description="Destination file path on Google Drive in the POSIX format. "
                                    "For example, 'foo/bar/baz.txt'"
                    ): str,
                    Literal(
                        "text",
                        description="Text to be appended to the Google Doc."
                    ): str
                }
            ),
        }
    )
    def append_text_to_google_doc(self, params: dict) -> InfoArtifact | ErrorArtifact:
        try:
            file_path = params["file_path"]
            text = params["text"]
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
                return InfoArtifact("text appended successfully")
            else:
                return ErrorArtifact(f"error appending to Google Doc, file not found for path {file_path}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error appending text to Google Doc with path {file_path}: {e}")

    @activity(
        config={
            "description": "Can be used to prepend text to a Google Doc",
            "schema": Schema(
                {
                    Literal(
                        "file_path",
                        description="Destination file path on Google Drive in the POSIX format. "
                                    "For example, 'foo/bar/baz.txt'"
                    ): str,
                    Literal(
                        "text",
                        description="Text to be prepended to the Google Doc."
                    ): str
                }
            ),
        }
    )
    def prepend_text_to_google_doc(self, params: dict) -> InfoArtifact | ErrorArtifact:
        try:
            file_path = params["file_path"]
            text = params["text"]
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
                return InfoArtifact("text prepended successfully")
            else:
                return ErrorArtifact(f"error prepending to google doc, file not found for path {file_path}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error prepending text to Google Doc with path {file_path}: {e}")

    @activity(
        config={
            "description": "Can be used to create a new Google Doc and save content to it on Google Drive",
            "schema": Schema(
                {
                    Literal(
                        "file_path",
                        description="Name of the file to be created, which will be used to save content in."
                    ): str,
                    Literal(
                        "content",
                        description="Content to be saved in Google Doc."
                    ): str
                }
            ),
        }
    )
    def save_content_to_google_doc(self, params: dict) -> ErrorArtifact | InfoArtifact:
        doc_creation_result = self.create_google_doc({"file_name": params["file_name"]})
    
        if isinstance(doc_creation_result, ErrorArtifact):
            return ErrorArtifact(f"error creating Google Doc: {doc_creation_result.value}")
    
        document_id = doc_creation_result.value.split()[-1]
        save_content_params = {"document_id": document_id, "content": params["content"]}
    
        try:
            saved_document_id = self._save_to_doc(save_content_params)
            return InfoArtifact(saved_document_id)
        except Exception as e:
            return ErrorArtifact(f"error saving content to Google Doc with Id {document_id}: {str(e)}")

    @activity(
        config={
            "description": "Can be used to download multiple Google Docs from Google Drive based on their paths.",
            "schema": Schema(
                {
                    Literal(
                        "file_paths",
                        description="Destination file paths on Google Drive in the POSIX format. "
                                    "For example, 'foo/bar/baz.txt, foo/bar/baz2.txt'"
                    ): [str]
                }
            ),
        }
    )
    def download_google_docs(self, params: dict) -> ListArtifact | ErrorArtifact:
        file_paths = params["file_paths"]
        downloaded_files = []

        for file_path in file_paths:
            document_artifact = self._download_document(file_path)
            if isinstance(document_artifact, ErrorArtifact):
                return ErrorArtifact(f"error downloading Google Doc for path {file_path}: {document_artifact.value}")
            downloaded_files.append(document_artifact)

        return ListArtifact(downloaded_files)

    def _download_document(self, file_path: str) -> BlobArtifact | ErrorArtifact:

        try:
            service = self._build_client(self.DRIVE_SCOPES, "v3", "drive")
            file_id = self._path_to_file_id(service, file_path)
            if file_id:
                results = service.files().list(q=f"name='{file_path}'", spaces="drive", pageSize=10).execute()
                items = results.get("files", [])
                if items:
                    file_id = items[0]["id"]
                    request = service.files().export(fileId=file_id, mimeType="text/plain")
                    response = request.execute()
                    return BlobArtifact(response)
                else:
                    return ErrorArtifact(f"Error: File not found for path {file_path}")
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
    
            if not files:
                if idx != len(parts) - 1:
                    folder_metadata = {
                        "name": part,
                        "mimeType": "application/vnd.google-apps.folder",
                        "parents": [current_id],
                    }
                    folder = service.files().create(body=folder_metadata, fields="id").execute()
                    current_id = folder.get("id")
                else:
                    current_id = None
            else:
                current_id = files[0]["id"]
    
        return current_id

    def _save_to_doc(self, params: dict) -> str:
        service = self._build_client(
            self.DOCS_SCOPES,
            version="v1",
            tool="docs",
        )
    
        requests = [
            {
                "insertText": {
                    "location": {
                        "index": 1,
                    },
                    "text": params["content"],
                }
            }
        ]
        service.documents().batchUpdate(documentId=params["document_id"], body={"requests": requests}).execute()
        return params["document_id"]
