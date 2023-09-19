from __future__ import annotations
from schema import Schema, Literal, Optional
from attr import define, field
from griptape.artifacts import ErrorArtifact, InfoArtifact, BlobArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient
from googleapiclient.errors import HttpError
from google.auth.exceptions import MalformedError
from googleapiclient.discovery import Resource
import logging


@define
class GoogleSheetsClient(BaseGoogleClient):
    owner_email: str = field(kw_only=True)
    SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    DRIVE_READ_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    DRIVE_UPLOAD_SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def _build_client(self, scopes: list[str], service_name: str, version: str) -> Resource:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(self.owner_email)
        service = build(service_name, version, credentials=delegated_credentials)
        return service

    def create_new_sheet(self, params: dict) -> InfoArtifact | ErrorArtifact:
        values = params["values"]
        title = values.get("title", "Untitled Sheet")

        try:
            service = self._build_client(self.SHEETS_SCOPES, 'sheets', 'v4')

            spreadsheet_body = {
                'properties': {'title': title}
            }

            spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
            return InfoArtifact(f"Spreadsheet created with ID: {spreadsheet['spreadsheetId']}")

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"Error creating a new sheet: {e}")

    def _resolve_path_to_id(self, service, path: str) -> Optional[str]:
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

    def download_sheet_as_csv_or_excel(self, params: dict) -> BlobArtifact | ErrorArtifact:
        values = params["values"]
        file_path = values["file_path"]
        mime_type = values["mime_type"]

        export_mime_mapping = {
            "text/csv": "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }

        if mime_type not in export_mime_mapping:
            return ErrorArtifact("Unsupported mime type for downloading")

        try:
            service = self._build_client(self.DRIVE_READ_SCOPES, service_name='drive', version='v3')
            sheet_id = self._resolve_path_to_id(service, file_path)

            if not sheet_id:
                return ErrorArtifact(f"Could not find sheet at path: {file_path}")

            request = service.files().export_media(fileId=sheet_id, mimeType=export_mime_mapping[mime_type])
            downloaded_file = request.execute()  # This fetches the file data

            return BlobArtifact(downloaded_file)  # Returns the file data wrapped in a BlobArtifact

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"Error downloading sheet at path {file_path}: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("Error downloading sheet due to malformed credentials")

    def upload_file_as_sheet(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.http import MediaFileUpload

        values = params['values']

        mime_mapping = {
            'csv': 'text/csv',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

        file_type = values['file_type']
        if file_type not in mime_mapping:
            logging.error(f"Unsupported file type '{file_type}' provided.")
            return ErrorArtifact(f"Unsupported file type '{file_type}'. Please provide either 'csv' or 'excel'.")

        try:
            service = self._build_client(self.DRIVE_UPLOAD_SCOPES, service_name='drive', version='v3')
            file_metadata = {
                'name': values['file_name'],
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            }
            media = MediaFileUpload(values['file_path'], mimetype=mime_mapping[values['file_type']])
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            return InfoArtifact(
                f'A file was successfully uploaded and converted to a Google Sheet with ID {file.get("id")}.')

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error uploading and converting file to Google Sheet: {e}")

