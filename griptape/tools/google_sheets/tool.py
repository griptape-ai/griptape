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
                    ): str
                }
            ),
        }
    )
    def list_spreadsheets(self, params: dict) -> ListArtifact | ErrorArtifact:
        from googleapiclient.errors import HttpError
        from google.auth.exceptions import MalformedError

        values = params["values"]
        folder_path = values.get("folder_path", self.DEFAULT_FOLDER_PATH)

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
                    return ErrorArtifact(
                        f"Could not find folder: {folder_path}"
                    )

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
                    spreadsheets.append(
                        InfoArtifact(
                            f"Spreadsheet ID: {file['id']}, Name: {file['name']}"
                        )
                    )

                page_token = response.get("nextPageToken")
            return ListArtifact(spreadsheets)

        except HttpError as e:
            return ErrorArtifact(
                f"error listing spreadsheet due to http error: {e}"
            )
        except MalformedError as e:
            return ErrorArtifact(
                f"error listing spreadsheet due to malformed credentials: {e}"
            )
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

        values = params["values"]
        title = values.get("title")

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

        values = params["values"]
        file_type = values.get("file_type")
        file_path = values.get("file_path")
        file_name = values.get("file_name")

        mime_mapping = {
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

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
                "name": file_name,
                "mimeType": "application/vnd.google-apps.spreadsheet",
            }
            media = MediaFileUpload(file_path, mimetype=mime_mapping[file_type])
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
            "description": "Can be used to modify a cell value in Google Sheets based on the specified operation "
            "(append, update, or delete).",
            "schema": Schema(
                {
                    Literal(
                        "file_path",
                        description="The file path of the spreadsheet to modify",
                    ): str,
                    Literal(
                        "range", description="The cell range to modify"
                    ): str,
                    Optional(
                        "values",
                        description="The values to be added or updated",
                    ): list,
                    Literal(
                        "operation",
                        description="The operation type (append, update, or delete)",
                    ): Or("append", "update", "delete"),
                }
            ),
        }
    )
    def modify_cell(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from google.auth.exceptions import MalformedError
        from googleapiclient.errors import HttpError

        input_values = params["values"]
        file_path = input_values.get("file_path")
        range_ = input_values.get("range")
        values = input_values.get("values")
        operation = input_values["operation"]

        try:
            sheets_service = self._build_client(
                scopes=self.SHEETS_SCOPES,
                service_name="sheets",
                version="v4",
                owner_email=self.owner_email,
            )
            drive_service = self._build_client(
                scopes=self.DRIVE_UPLOAD_SCOPES,
                service_name="drive",
                version="v3",
                owner_email=self.owner_email,
            )

            spreadsheet_id = self._convert_path_to_file_id(
                drive_service, file_path
            )

            if spreadsheet_id:
                if operation == "append":
                    sheets_service.spreadsheets().values().append(
                        spreadsheetId=spreadsheet_id,
                        range=range_,
                        valueInputOption="RAW",
                        body={"values": [values]},
                    ).execute()
                    result = InfoArtifact(
                        f"Value appended to {file_path} at range {range_}"
                    )
                elif operation == "update":
                    sheets_service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=range_,
                        valueInputOption="RAW",
                        body={"values": [values]},
                    ).execute()
                    result = InfoArtifact(
                        f"Value updated in {file_path} at range {range_}"
                    )
                elif operation == "delete":
                    sheets_service.spreadsheets().values().clear(
                        spreadsheetId=spreadsheet_id, range=range_
                    ).execute()
                    result = InfoArtifact(
                        f"Value cleared in {file_path} at range {range_}"
                    )
                else:
                    result = ErrorArtifact(
                        f"Unsupported operation: {operation}"
                    )
            else:
                result = ErrorArtifact(
                    f"Could not find spreadsheet: {file_path}"
                )

            return result

        except HttpError as e:
            return ErrorArtifact(
                f"error modifying value in cell due to http error: {e}"
            )
        except MalformedError as e:
            return ErrorArtifact(
                f"error modifying value in cell due to malformed credentials: {e}"
            )
        except Exception as e:
            return ErrorArtifact(f"error in modifying value in cell: {e}")
