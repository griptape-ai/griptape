from __future__ import annotations
import logging
from schema import Schema, Literal, Optional
from attr import define, field
from griptape.artifacts import TextArtifact, ErrorArtifact, InfoArtifact, ListArtifact, BlobArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient
from googleapiclient.errors import HttpError
from google.auth.exceptions import MalformedError
from googleapiclient.discovery import Resource

@define
class GoogleDriveClient(BaseGoogleClient):
    LIST_FILES_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    UPLOAD_FILE_SCOPES = ['https://www.googleapis.com/auth/drive.file']
    max_files: int = field(default=10, kw_only=True)

    def _build_client(self, scopes: list[str], values: dict) -> Resource:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(values["drive_owner_email"])
        service = build('drive', 'v3', credentials=delegated_credentials)
        return service

    @activity(config={
        "description": "Can be used to list files from Google Drive",
        "schema": Schema({
            Literal(
                "drive_owner_email",
                description="email of the Google Drive's owner"
            ): str,
            Optional(Literal(
                "max_files",
                description="maximum number of files to return"
            )): int
        })
    })
    def list_files(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES, values)

            folder_id = None
            if "folder_path" in values and values["folder_path"]:
                folder_id = self._resolve_path_to_id(service, values["folder_path"])
                if not folder_id:
                    return ErrorArtifact(f"Could not find folder: {values['folder_path']}")

            if folder_id:
                query = f"'{folder_id}' in parents and trashed=false"
            else:
                query = "mimeType != 'application/vnd.google-apps.folder' and 'root' in parents and trashed=false"

            # Use the provided max_files from the values dictionary, otherwise use the class default
            max_files = values.get("max_files", self.max_files)

            results = service.files().list(q=query, pageSize=max_files).execute()
            items = results.get('files', [])
            return ListArtifact(items)

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving files from Drive: {e}")

    def _resolve_path_to_id(self, service, path: str) -> Optional[str]:
        """Resolve a folder path to its Google Drive ID"""
        parts = path.split('/')
        current_id = 'root'

        for part in parts:
            response = service.files().list(
                q=f"name='{part}' and '{current_id}' in parents and mimeType='application/vnd.google-apps.folder'").execute()
            files = response.get('files', [])

            if not files:
                return None
            current_id = files[0]['id']

        return current_id

    @activity(config={
        "description": "Can be used to upload a file to Google Drive",
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
                description="name to give the file on Google Drive"
            ): str,
            Literal(
                "mime_type",
                description="MIME type of the file being uploaded"
            ): str
        })
    })
    def upload_file(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.http import MediaFileUpload

        values = params['values']

        try:
            service = self._build_client(self.UPLOAD_FILE_SCOPES, values)
            file_metadata = {'name': values['file_name']}
            media = MediaFileUpload(values['file_path'], mimetype=values['mime_type'])
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            return InfoArtifact(f'A file was successfully uploaded with ID {file.get("id")}.')

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error uploading file to Drive: {e}")

    @activity(config={
        "description": "Can be used to download a file from Google Drive",
        "schema": Schema({
            Literal(
                "drive_owner_email",
                description="email of the Google Drive's owner"
            ): str,
            Literal(
                "file_id",
                description="ID of the file to be downloaded from Google Drive"
            ): str
        })
    })
    def download_file(self, params: dict) -> BlobArtifact | ErrorArtifact:

        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES, values)
            request = service.files().get_media(fileId=values["file_id"])
            downloaded_file = request.execute()

            return BlobArtifact(downloaded_file)

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"error downloading file from Drive: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error downloading file due to malformed credentials")

    @activity(config={
        "description": "Can be used to search for a file in Google Drive",
        "schema": Schema({
            Literal(
                "drive_owner_email",
                description="email of the Google Drive's owner"
            ): str,
            Literal(
                "file_name",
                description="name of the file to search for in Google Drive"
            ): str
        })
    })
    def search_file(self, params: dict) -> ListArtifact | ErrorArtifact:

        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES, values)
            query = f"name='{values['file_name']}'"
            results = service.files().list(q=query).execute()
            items = results.get('files', [])
            return ListArtifact(items)

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"error searching for file in Drive: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error searching for file due to malformed credentials")