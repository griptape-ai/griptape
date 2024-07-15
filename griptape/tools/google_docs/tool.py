from __future__ import annotations

import logging

from attrs import define, field
from schema import Literal, Optional, Schema

from griptape.artifacts import ErrorArtifact, InfoArtifact
from griptape.tools import BaseGoogleClient
from griptape.utils.decorators import activity


@define
class GoogleDocsClient(BaseGoogleClient):
    DOCS_SCOPES = ["https://www.googleapis.com/auth/documents"]

    DEFAULT_FOLDER_PATH = "root"

    owner_email: str = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to append text to a Google Doc.",
            "schema": Schema(
                {
                    Literal(
                        "file_path",
                        description="Destination file path of Google Doc in the POSIX format. "
                        "For example, 'foo/bar/baz.txt'",
                    ): str,
                    Literal("text", description="Text to be appended to the Google Doc."): str,
                },
            ),
        },
    )
    def append_text_to_google_doc(self, params: dict) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        file_path = values.get("file_path")
        text = values.get("text")

        try:
            docs_service = self._build_client(
                scopes=self.DOCS_SCOPES,
                service_name="docs",
                version="v1",
                owner_email=self.owner_email,
            )
            drive_service = self._build_client(
                scopes=self.DRIVE_FILE_SCOPES,
                service_name="drive",
                version="v3",
                owner_email=self.owner_email,
            )

            document_id = self._convert_path_to_file_id(drive_service, file_path)
            if document_id:
                doc = docs_service.documents().get(documentId=document_id).execute()
                content = doc["body"]["content"]
                last_text = content[-1]["paragraph"]["elements"][-1]["textRun"]["content"]
                append_index = content[-1]["endIndex"]
                if last_text.endswith("\n"):
                    append_index -= 1

                requests = [{"insertText": {"location": {"index": append_index}, "text": text}}]

                docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
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
                        description="Destination file path of Google Doc in the POSIX format. "
                        "For example, 'foo/bar/baz.txt'",
                    ): str,
                    Literal("text", description="Text to be prepended to the Google Doc."): str,
                },
            ),
        },
    )
    def prepend_text_to_google_doc(self, params: dict) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        file_path = values.get("file_path")
        text = values.get("text")

        try:
            docs_service = self._build_client(
                scopes=self.DOCS_SCOPES,
                service_name="docs",
                version="v1",
                owner_email=self.owner_email,
            )
            drive_service = self._build_client(
                scopes=self.DRIVE_FILE_SCOPES,
                service_name="drive",
                version="v3",
                owner_email=self.owner_email,
            )

            document_id = self._convert_path_to_file_id(drive_service, file_path)
            if document_id:
                doc = docs_service.documents().get(documentId=document_id).execute()

                if len(doc["body"]["content"]) == 1:
                    requests = [{"insertText": {"location": {"index": 1}, "text": text}}]
                else:
                    start_index = doc["body"]["content"][1]["startIndex"]
                    requests = [{"insertText": {"location": {"index": start_index}, "text": text}}]

                docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
                return InfoArtifact("text prepended successfully")
            else:
                return ErrorArtifact(f"error prepending to google doc, file not found for path {file_path}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error prepending text to Google Doc with path {file_path}: {e}")

    @activity(
        config={
            "description": "Can be used to create a new Google Doc and optionally save content to it.",
            "schema": Schema(
                {
                    Literal(
                        "file_path",
                        description="Name of the file to be created, which will be used to save content in.",
                    ): str,
                    Optional("content", default=None, description="Optional content to be saved in Google Doc."): str,
                    Optional(
                        "folder_path",
                        default=DEFAULT_FOLDER_PATH,
                        description="Path of the folder where the Google doc will be created.",
                    ): str,
                },
            ),
        },
    )
    def save_content_to_google_doc(self, params: dict) -> ErrorArtifact | InfoArtifact:
        values = params["values"]
        file_path = values.get("file_path")
        content = values.get("content")
        folder_path = values.get("folder_path", self.DEFAULT_FOLDER_PATH)

        try:
            docs_service = self._build_client(
                scopes=self.DOCS_SCOPES,
                service_name="docs",
                version="v1",
                owner_email=self.owner_email,
            )
            drive_service = self._build_client(
                scopes=self.DRIVE_FILE_SCOPES,
                service_name="drive",
                version="v3",
                owner_email=self.owner_email,
            )

            body = {"title": file_path}

            doc = docs_service.documents().create(body=body).execute()
            doc_id = doc["documentId"]

            if folder_path.lower() != self.DEFAULT_FOLDER_PATH:
                folder_id = self._convert_path_to_file_id(drive_service, folder_path)
                if folder_id:
                    drive_service.files().update(fileId=doc_id, addParents=folder_id, fields="id, parents").execute()
                else:
                    return ErrorArtifact(f"Error: Folder not found for path {folder_path}")

            if content:
                save_content_params = {"document_id": doc_id, "content": content}
                saved_document_id = self._save_to_doc(save_content_params)
                return InfoArtifact(f"Content has been successfully saved to Google Doc with ID: {saved_document_id}.")
            else:
                return InfoArtifact(f"Google Doc '{file_path}' created with ID: {doc_id}")

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error creating/saving Google Doc: {e}")

    @activity(
        config={
            "description": "Can be used to load content from memory and save it to a new Google Doc "
            "in the specified folder.",
            "schema": Schema(
                {
                    "memory_name": str,
                    "artifact_namespace": str,
                    "file_name": str,
                    Optional(
                        "folder_path",
                        description="Path of the folder where the Google Doc should be saved.",
                        default=DEFAULT_FOLDER_PATH,
                    ): str,
                },
            ),
        },
    )
    def save_memory_artifacts_to_google_docs(self, params: dict) -> ErrorArtifact | InfoArtifact:
        values = params["values"]
        memory = self.find_input_memory(values["memory_name"])

        if memory:
            artifacts = memory.load_artifacts(values["artifact_namespace"])

            if artifacts:
                try:
                    file_path = values["file_name"]
                    content = "\n".join([a.value for a in artifacts])

                    save_params = {
                        "file_path": file_path,
                        "content": content,
                        "folder_path": values.get("folder_path", self.DEFAULT_FOLDER_PATH),
                    }

                    return self.save_content_to_google_doc(save_params)

                except Exception as e:
                    return ErrorArtifact(f"Error: {e}")

            else:
                return ErrorArtifact("no artifacts found")
        else:
            return ErrorArtifact("memory not found")

    def _save_to_doc(self, params: dict) -> str:
        service = self._build_client(
            scopes=self.DOCS_SCOPES,
            service_name="docs",
            version="v1",
            owner_email=self.owner_email,
        )

        requests = [{"insertText": {"location": {"index": 1}, "text": params["content"]}}]
        service.documents().batchUpdate(documentId=params["document_id"], body={"requests": requests}).execute()
        return params["document_id"]
