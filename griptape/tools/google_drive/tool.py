from __future__ import annotations
import logging
from schema import Schema, Literal, Optional
from attr import define, field
from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, BlobArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient
from googleapiclient.errors import HttpError
from google.auth.exceptions import MalformedError
from googleapiclient.discovery import Resource

@define
class GoogleDriveClient(BaseGoogleClient):
    owner_email: str = field(kw_only=True)

    LIST_FILES_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    UPLOAD_FILE_SCOPES = ['https://www.googleapis.com/auth/drive.file']

    GOOGLE_EXPORT_MIME_MAPPING = {
        "application/vnd.google-apps.document":
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.google-apps.spreadsheet":
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.google-apps.presentation":
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    }

    page_size: int = field(default=100, kw_only=True)

    def _build_client(self, scopes: list[str]) -> Resource:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(self.owner_email)
        service = build('drive', 'v3', credentials=delegated_credentials)

        return service

    def _path_to_file_id(self, service, path: str) -> Optional[str]:
        parts = path.split('/')
        current_id = 'root'

        for index, part in enumerate(parts):
            if index == len(parts) - 1:
                query = f"name='{part}' and '{current_id}' in parents"
            else:
                query = f"name='{part}' and '{current_id}' in parents and mimeType='application/vnd.google-apps.folder'"

            response = service.files().list(q=query).execute()
            files = response.get('files', [])

            if not files:
                return None
            current_id = files[0]['id']

        return current_id

    def list_files(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES)

            folder_id = None
            if "folder_path" in values and values["folder_path"]:
                folder_id = self._path_to_file_id(service, values["folder_path"])
                if not folder_id:
                    return ErrorArtifact(f"Could not find folder: {values['folder_path']}")

            if folder_id:
                query = f"'{folder_id}' in parents and trashed=false"
            else:
                query = "mimeType != 'application/vnd.google-apps.folder' and 'root' in parents and trashed=false"

            user_max_files = values.get("max_files")
            max_files = self.page_size if user_max_files is None else user_max_files

            items = []
            next_page_token = None

            while True:
                results = service.files().list(
                    q=query,
                    pageSize=max_files,
                    pageToken=next_page_token,
                ).execute()

                files = results.get('files', [])
                items.extend(files)

                next_page_token = results.get('nextPageToken')

                if not next_page_token:
                    break

            return ListArtifact(items)

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving files from Drive: {e}")

    def upload_file(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.http import MediaFileUpload

        values = params['values']

        try:
            service = self._build_client(self.UPLOAD_FILE_SCOPES)
            file_metadata = {'name': values['file_name']}
            media = MediaFileUpload(values['file_path'], mimetype=values['mime_type'])
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            return InfoArtifact(f'A file was successfully uploaded with ID {file.get("id")}.')

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error uploading file to Drive: {e}")

    def download_file(self, params: dict) -> BlobArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES)
            file_id = self._path_to_file_id(service, values["file_path"])
            if not file_id:
                return ErrorArtifact(f"Could not find file: {values['file_path']}")

            file_info = service.files().get(fileId=file_id).execute()
            mime_type = file_info['mimeType']

            if mime_type in self.GOOGLE_EXPORT_MIME_MAPPING:
                export_mime = self.GOOGLE_EXPORT_MIME_MAPPING[mime_type]
                request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            else:
                request = service.files().get_media(fileId=file_id)

            downloaded_file = request.execute()
            logging.info(f"File '{values['file_path']}' successfully downloaded.")
            return BlobArtifact(downloaded_file)

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"error downloading file from Drive: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error downloading file due to malformed credentials")

    def search_file(self, params: dict) -> ListArtifact | ErrorArtifact:

        values = params["values"]

        try:
            service = self._build_client(self.LIST_FILES_SCOPES)
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