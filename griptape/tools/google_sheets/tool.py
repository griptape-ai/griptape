from __future__ import annotations
import logging
from schema import Schema, Literal, Optional, Or
from attr import define, field
from griptape.artifacts import (
    ErrorArtifact,
    InfoArtifact,
    ListArtifact,
    BlobArtifact,
)
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient


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
        from googleapiclient.errors import HttpError
        from google.auth.exceptions import MalformedError
    
        folder_path = params.get("folder_path", self.DEFAULT_FOLDER_PATH)
    
        try:
            service = self._build_client(
                scopes=self.DRIVE_READ_SCOPES,
                service_name="drive",
                version="v3",
                owner_email=self.owner_email,
            )
    
            if folder_path == self.DEFAULT_FOLDER_PATH:
                query = "mimeType='application/vnd.google-apps.spreadsheet' and 'root' in parents and trashed=false"
            else:
                folder_id = self._convert_path_to_file_id(service, folder_path)
                if folder_id:
                    query = (
                        f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' "
                        f"and trashed=false"
                    )
                else:
                    return ErrorArtifact(f"Could not find folder: {folder_path}")
    
            spreadsheets = []
            page_token = None
    
            while page_token is not None:
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
    
                page_token = response.get("nextPageToken")
            return ListArtifact(spreadsheets)
    
        except HttpError as e:
            return ErrorArtifact(f"error listing spreadsheet due to http error: {e}")
        except MalformedError as e:
            return ErrorArtifact(f"error listing spreadsheet due to malformed credentials: {e}")
        except Exception as e:
            return ErrorArtifact(f"error listing spreadsheets: {e}")

    @activity(
        config={
            "description": "Can be used to creates a new Google Sheet with the specified title.",
            "schema": Schema(
                {
                    Literal(
                        "title", description="The title of the new spreadsheet"
                    ): str
                }
            ),
        }
    )
    def create_spreadsheet(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.errors import HttpError
        from google.auth.exceptions import MalformedError

        title = params["title"]

        try:
            service = self._build_client(
                scopes=self.SHEETS_SCOPES,
                service_name="sheets",
                version="v4",
                owner_email=self.owner_email,
            )

            spreadsheet_body = {"properties": {"title": title}}

            spreadsheet = (
                service.spreadsheets().create(body=spreadsheet_body).execute()
            )
            return InfoArtifact(
                f"Spreadsheet created with ID: {spreadsheet['spreadsheetId']}"
            )

        except HttpError as e:
            return ErrorArtifact(
                f"error creating spreadsheet due to http error: {e}"
            )
        except MalformedError as e:
            return ErrorArtifact(
                f"error creating spreadsheet due to malformed credentials: {e}"
            )
        except Exception as e:
            return ErrorArtifact(f"error creating spreadsheets: {e}")

    @activity(
        config={
            "description": "Can be used to downloads multiple spreadsheets based on provided file paths",
            "schema": Schema(
                {
                    Literal(
                        "file_paths",
                        description="List of file paths to the spreadsheets.",
                    ): list[str],
                    Literal(
                        "mime_type",
                        description="The MIME type for the file format to export to.",
                    ): str,
                }
            ),
        }
    )
    def download_spreadsheets(self, params: dict) -> ListArtifact | ErrorArtifact:
        from google.auth.exceptions import MalformedError
        from googleapiclient.errors import HttpError

        file_paths = params["file_paths"]
        mime_type = params["mime_type"]

        export_mime_mapping = {
            "text/csv": "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        downloaded_files = []

        if mime_type not in export_mime_mapping:
            logging.error(f"Unsupported mime type '{mime_type}' provided.")
            return ErrorArtifact("Unsupported mime type for downloading")
        else:
            try:
                service = self._build_client(
                    scopes=self.DRIVE_READ_SCOPES,
                    service_name="drive",
                    version="v3",
                    owner_email=self.owner_email,
                )
                for file_path in file_paths:
                    sheet_id = self._convert_path_to_file_id(service, file_path)

                    if sheet_id:
                        request = service.files().export_media(
                            fileId=sheet_id,
                            mimeType=export_mime_mapping[mime_type],
                        )
                        downloaded_files.append(BlobArtifact(request.execute()))
                    else:
                        logging.error(
                            f"error finding spreadsheet at path: {file_path}"
                        )

            except HttpError as e:
                return ErrorArtifact(
                    f"error downloading spreadsheet due to http error: {e}"
                )
            except MalformedError as e:
                return ErrorArtifact(
                    f"error downloading spreadsheet due to malformed credentials: {e}"
                )
            except Exception as e:
                return ErrorArtifact(f"error downloading spreadsheets: {e}")

        return ListArtifact(downloaded_files)

    @activity(
        config={
            "description": "Uploads a spreadsheet and converts it to a Google Sheets format",
            "schema": Schema(
                {
                    Literal(
                        "file_name",
                        description="The name of the file to be uploaded",
                    ): str,
                    Literal(
                        "file_path",
                        description="The local path to the file to be uploaded",
                    ): str,
                    Literal(
                        "file_type",
                        description="The type of the file being uploaded, e.g., 'csv' or 'excel'",
                    ): str,
                }
            ),
        }
    )
    def upload_spreadsheet(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from googleapiclient.http import MediaFileUpload
        from google.auth.exceptions import MalformedError
        from googleapiclient.errors import HttpError

        mime_mapping = {
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        file_type = params["file_type"]
        if file_type not in mime_mapping:
            logging.error(f"Unsupported file type '{file_type}' provided.")
            return ErrorArtifact(
                f"Unsupported file type '{file_type}'. Please provide either 'csv' or 'excel'."
            )

        try:
            service = self._build_client(
                scopes=self.DRIVE_UPLOAD_SCOPES,
                service_name="drive",
                version="v3",
                owner_email=self.owner_email,
            )

            file_metadata = {
                "name": params["file_name"],
                "mimeType": "application/vnd.google-apps.spreadsheet",
            }
            media = MediaFileUpload(
                params["file_path"], mimetype=mime_mapping[params["file_type"]]
            )
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            return InfoArtifact(
                f'file was successfully uploaded and converted to a Google Sheet with ID {file.get("id")}.'
            )
        except HttpError as e:
            return ErrorArtifact(
                f"error uploading spreadsheet due to http error: {e}"
            )
        except MalformedError as e:
            return ErrorArtifact(
                f"error uploading spreadsheet due to malformed credentials: {e}"
            )
        except Exception as e:
            return ErrorArtifact(
                f"error uploading and converting file to Google Sheet: {e}"
            )

    @activity(
        config={
            "description": "Can be used to share a spreadsheet with a specified user.",
            "schema": Schema(
                {
                    Literal(
                        "file_path",
                        description="The path of the spreadsheet to share",
                    ): str,
                    Literal(
                        "email_address",
                        description="The email address of the user to share with",
                    ): str,
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
        from google.auth.exceptions import MalformedError
        from googleapiclient.errors import HttpError

        file_path = params["file_path"]
        email_address = params["email_address"]
        role = params.get("role", "reader")

        try:
            service = self._build_client(
                scopes=self.DRIVE_AUTH_SCOPES,
                service_name="drive",
                version="v3",
                owner_email=self.owner_email,
            )

            if file_path.lower() == self.DEFAULT_FOLDER_PATH:
                spreadsheet_id = self.DEFAULT_FOLDER_PATH
            else:
                spreadsheet_id = self._convert_path_to_file_id(
                    service, file_path
                )

            if spreadsheet_id:
                batch_update_permission_request_body = {
                    "role": role,
                    "type": "user",
                    "emailAddress": email_address,
                }
                request = service.permissions().create(
                    fileId=spreadsheet_id,
                    body=batch_update_permission_request_body,
                    fields="id",
                )
                request.execute()
                return InfoArtifact(
                    f"Spreadsheet at {file_path} shared with {email_address} as a {role}"
                )
            else:
                return ErrorArtifact(
                    f"error finding spreadsheet at path: {file_path}"
                )
        except HttpError as e:
            return ErrorArtifact(
                f"error sharing spreadsheet due to http error: {e}"
            )
        except MalformedError as e:
            return ErrorArtifact(
                f"error sharing spreadsheet due to malformed credentials: {e}"
            )
        except Exception as e:
            return ErrorArtifact(f"error sharing spreadsheet: {e}")

    @activity(
        config={
            "description": "Can be used to check the permissions on a specified spreadsheet.",
            "schema": Schema(
                {
                    Literal(
                        "file_path",
                        description="The path of the spreadsheet to check permissions for",
                    ): str,
                }
            ),
        }
    )
    def list_permissions_for_spreadsheet(self, params: dict) -> ListArtifact | ErrorArtifact:
        from google.auth.exceptions import MalformedError
        from googleapiclient.errors import HttpError

        file_path = params["file_path"]

        try:
            service = self._build_client(
                scopes=self.DRIVE_AUTH_SCOPES,
                service_name="drive",
                version="v3",
                owner_email=self.owner_email,
            )
            if file_path.lower() == self.DEFAULT_FOLDER_PATH:
                spreadsheet_id = self.DEFAULT_FOLDER_PATH
            else:
                spreadsheet_id = self._convert_path_to_file_id(
                    service, file_path
                )

            if spreadsheet_id:
                permissions = (
                    service.permissions()
                    .list(
                        fileId=spreadsheet_id,
                        fields="permissions(id,role,emailAddress)",
                    )
                    .execute()
                )

                permissions_artifacts = [
                    InfoArtifact(
                        f"Permission ID: {perm['id']}, Role: {perm['role']}, Email: {perm['emailAddress']}"
                    )
                    for perm in permissions.get("permissions", [])
                ]

                return ListArtifact(permissions_artifacts)
            else:
                return ErrorArtifact(
                    f"error finding spreadsheet at path: {file_path}"
                )
        except HttpError as e:
            return ErrorArtifact(
                f"error checking permissions due to http error: {e}"
            )
        except MalformedError as e:
            return ErrorArtifact(
                f"error checking permissions due to malformed credentials: {e}"
            )
        except Exception as e:
            return ErrorArtifact(f"error checking permissions: {e}")
