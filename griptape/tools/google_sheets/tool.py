from __future__ import annotations
from typing import Any, TYPE_CHECKING
import logging
from schema import Schema, Literal, Optional, Or
from attr import define, field
from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, BlobArtifact, TextArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


@define
class GoogleSheetsClient(BaseGoogleClient):
    SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    DRIVE_READ_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

    DRIVE_AUTH_SCOPES = ["https://www.googleapis.com/auth/drive"]

    DRIVE_UPLOAD_SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    DEFAULT_FOLDER_PATH = "root"

    owner_email: str = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to list all spreadsheets in the specified folder.",
            "schema": Schema(
                {
                    Optional(
                        "folder_path",
                        default=DEFAULT_FOLDER_PATH,
                        description="Path of the folder (like 'MainFolder/Subfolder1/Subfolder2') "
                        "from which spreadsheets should be listed.",
                    ): str,
                }
            ),
        }
    )
    def list_spreadsheets(self, params: dict) -> ListArtifact | ErrorArtifact:
        folder_path = params.get("folder_path", self.DEFAULT_FOLDER_PATH)
        service = self._build_client(self.DRIVE_READ_SCOPES, service_name="drive", version="v3")

        try:
            if folder_path == self.DEFAULT_FOLDER_PATH:
                query = "mimeType='application/vnd.google-apps.spreadsheet' and 'root' in parents and trashed=false"
            else:
                folder_id = self._path_to_file_id(service, folder_path)
                if folder_id:
                    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
                else:
                    return ErrorArtifact(f"Could not find folder: {folder_path}")

            spreadsheets = []
            page_token = None

            while True:
                response = (
                    service.files()
                    .list(
                        q=query,
                        spaces="drive",
                        fields="nextPageToken, files(id, name)",
                        pageToken=page_token,
                    )
                    .execute()
                )

                for file in response.get("files", []):
                    spreadsheets.append(InfoArtifact(f"Spreadsheet ID: {file['id']}, Name: {file['name']}"))

                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error listing spreadsheets: {e}")

        return ListArtifact(spreadsheets)

    @activity(
        config={
            "description": "Can be used to creates a new Google Sheet with the specified title.",
            "schema": Schema({Literal("title", description="The title of the new spreadsheet"): str}),
        }
    )
    def create_spreadsheet(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.errors import HttpError

        title = params["title"]

        try:
            service = self._build_client(self.SHEETS_SCOPES, "sheets", "v4")

            spreadsheet_body = {"properties": {"title": title}}

            spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
            return InfoArtifact(f"Spreadsheet created with ID: {spreadsheet['spreadsheetId']}")

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"Error creating a new sheet: {e}")

    @activity(
        config={
            "description": "Can be used to downloads multiple spreadsheets based on provided file paths",
            "schema": Schema(
                {
                    Literal("file_paths", description="List of file paths to the spreadsheets."): [str],
                    Literal("mime_type", description="The MIME type for the file format to export to."): str,
                }
            ),
        }
    )
    def download_spreadsheets(self, params: dict) -> ListArtifact:
        from google.auth.exceptions import MalformedError
        from googleapiclient.errors import HttpError

        file_paths = params["file_paths"]  # Expecting a list of file paths
        mime_type = params["mime_type"]

        export_mime_mapping = {
            "text/csv": "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        downloaded_files = []

        if mime_type not in export_mime_mapping:
            logging.error("Unsupported mime type for downloading")
        else:
            service = self._build_client(self.DRIVE_READ_SCOPES, service_name="drive", version="v3")
            for file_path in file_paths:
                try:
                    sheet_id = self._path_to_file_id(service, file_path)

                    if sheet_id:
                        request = service.files().export_media(fileId=sheet_id, mimeType=export_mime_mapping[mime_type])
                        downloaded_files.append(
                            BlobArtifact(request.execute())
                        )
                    else:
                        logging.error(f"Could not find sheet at path: {file_path}")

                except HttpError as e:
                    logging.error(e)

                except MalformedError:
                    logging.error(f"MalformedError occurred while downloading sheet '{file_path}'")

        return ListArtifact(downloaded_files)

    @activity(
        config={
            "description": "Uploads a spreadsheet and converts it to a Google Sheets format",
            "schema": Schema(
                {
                    Literal("file_name", description="The name of the file to be uploaded"): str,
                    Literal("file_path", description="The local path to the file to be uploaded"): str,
                    Literal(
                        "file_type", description="The type of the file being uploaded, e.g., 'csv' or 'excel'"
                    ): str,
                }
            ),
        }
    )
    def upload_spreadsheet(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.http import MediaFileUpload

        mime_mapping = {"csv": "text/csv", "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}

        file_type = params["file_type"]
        if file_type not in mime_mapping:
            logging.error(f"Unsupported file type '{file_type}' provided.")
            return ErrorArtifact(f"Unsupported file type '{file_type}'. Please provide either 'csv' or 'excel'.")

        try:
            service = self._build_client(self.DRIVE_UPLOAD_SCOPES, service_name="drive", version="v3")
            file_metadata = {"name": params["file_name"], "mimeType": "application/vnd.google-apps.spreadsheet"}
            media = MediaFileUpload(params["file_path"], mimetype=mime_mapping[params["file_type"]])
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            return InfoArtifact(
                f'A file was successfully uploaded and converted to a Google Sheet with ID {file.get("id")}.'
            )

        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error uploading and converting file to Google Sheet: {e}")

    @activity(
        config={
            "description": "Can be used to share a spreadsheet with a specified user.",
            "schema": Schema(
                {
                    Literal("file_path", description="The path of the spreadsheet to share"): str,
                    Literal("email_address", description="The email address of the user to share with"): str,
                    Optional(
                        "role",
                        default="reader",
                        description="The role to give to the user, e.g., 'reader', 'writer', or 'commenter'",
                    ): Or("reader", "writer", "commenter"),
                }
            ),
        }
    )
    def share_spreadsheet(self, params: dict) -> InfoArtifact | ErrorArtifact:
        file_path = params["file_path"]
        email_address = params["email_address"]
        role = params.get("role", "reader")

        try:
            service = self._build_client(self.DRIVE_AUTH_SCOPES, service_name="drive", version="v3")

            if file_path.lower() == self.DEFAULT_FOLDER_PATH:
                spreadsheet_id = self.DEFAULT_FOLDER_PATH
            else:
                spreadsheet_id = self._path_to_file_id(service, file_path)

            if spreadsheet_id:
                batch_update_permission_request_body = {"role": role, "type": "user", "emailAddress": email_address}
                request = service.permissions().create(
                    fileId=spreadsheet_id, body=batch_update_permission_request_body, fields="id"
                )
                request.execute()
                return InfoArtifact(f"Spreadsheet at {file_path} shared with {email_address} as a {role}")
            else:
                return ErrorArtifact(f"No spreadsheet found at path: {file_path}")
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error sharing spreadsheet: {e}")

    @activity(
        config={
            "description": "Can be used to check the permissions on a specified spreadsheet.",
            "schema": Schema(
                {
                    Literal("file_path", description="The path of the spreadsheet to check permissions for"): str,
                }
            ),
        }
    )
    def check_permissions_for_spreadsheet(self, params: dict) -> ListArtifact | ErrorArtifact:
        file_path = params["file_path"]
        service = self._build_client(self.DRIVE_AUTH_SCOPES, service_name="drive", version="v3")

        try:
            if file_path.lower() == self.DEFAULT_FOLDER_PATH:
                spreadsheet_id = self.DEFAULT_FOLDER_PATH
            else:
                spreadsheet_id = self._path_to_file_id(service, file_path)

            if spreadsheet_id:
                permissions = (
                    service.permissions()
                    .list(fileId=spreadsheet_id, fields="permissions(id,role,emailAddress)")
                    .execute()
                )

                permissions_artifacts = [
                    InfoArtifact(f"Permission ID: {perm['id']}, Role: {perm['role']}, Email: {perm['emailAddress']}")
                    for perm in permissions.get("permissions", [])
                ]

                return ListArtifact(permissions_artifacts)
            else:
                return ErrorArtifact(f"No spreadsheet found at path: {file_path}")
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"Error checking permissions: {e}")

    def _build_client(self, scopes: list[str], service_name: str, version: str) -> Resource:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(self.owner_email)
        service = build(service_name, version, credentials=delegated_credentials)
        return service

    def _path_to_file_id(self, service, path: str) -> Optional[str]:
        parts = path.split("/")
        current_id = self.DEFAULT_FOLDER_PATH

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
