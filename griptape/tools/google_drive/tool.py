from __future__ import annotations
import logging
from schema import Schema, Literal, Optional
from attr import define
from griptape.artifacts import TextArtifact, ErrorArtifact, InfoArtifact, ListArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient
from googleapiclient.errors import HttpError
from google.auth.exceptions import MalformedError


@define
class GoogleDriveClient(BaseGoogleClient):
    LIST_FILES_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    UPLOAD_FILE_SCOPES = ['https://www.googleapis.com/auth/drive.file']

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
    def _build_client(self, scopes: list[str], values: dict) -> object:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(values["drive_owner_email"])
        service = build('drive', 'v3', credentials=delegated_credentials)
        return service

    def list_files(self, params: dict) -> ListArtifact | ErrorArtifact:

        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES, values)
            results = service.files().list(pageSize=values.get('max_files', 10)).execute()
            items = results.get('files', [])
            return items

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving files from Drive: {e}")

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
    def download_file(self, params: dict) -> TextArtifact | ErrorArtifact:

        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES, values)
            request = service.files().get_media(fileId=values["file_id"])
            downloaded_file = request.execute()

            return TextArtifact(downloaded_file)

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

            return items

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"error searching for file in Drive: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error searching for file due to malformed credentials")