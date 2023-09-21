from __future__ import annotations
import logging
from schema import Schema, Literal, Optional
from attr import define, field
from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, BlobArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient, BaseTool
from google.auth.exceptions import MalformedError
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from io import BytesIO

@define
class GoogleDriveClient(BaseGoogleClient, BaseTool):
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

    owner_email: str = field(kw_only=True)
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

    @activity(config={
        "description": "List files in a specific Google Drive folder or the root if no folder is specified",
        "schema": Schema({
            Optional("folder_path",
                     description="Path of the Google Drive folder (like 'MainFolder/Subfolder1/Subfolder2') "
                                 "from which files should be listed. If not provided, files from the root "
                                 "directory will be listed."): str,
            Optional("max_files",
                     description="Maximum number of files to list. If not provided, the default page size will be used."): int
        })
    })
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
            return ErrorArtifact(f"error retrieving files from Google Drive: {e}")

    @activity(config={
        "description": "Can be used to save memory artifacts to Google Drive using folder paths",
        "schema": Schema({
            "memory_name": str,
            "artifact_namespace": str,
            "file_name": str,
            Optional("folder_path",
                     description="Path of the Google Drive folder (like 'MainFolder/Subfolder1/Subfolder2') "
                                 "where the file should be stored. If not provided, the file will be saved "
                                 "to the root directory."): str,
        })
    })
    def save_memory_artifacts_to_drive(self, params: dict) -> ErrorArtifact | InfoArtifact:
        values = params["values"]
        memory = self.find_input_memory(values["memory_name"])
        file_name = values["file_name"]
    
        if memory:
            artifacts = memory.load_artifacts(values["artifact_namespace"])
    
            if not artifacts:
                return ErrorArtifact("no artifacts found")

            service = self._build_client(self.UPLOAD_FILE_SCOPES)

            folder_id = None
            if "folder_path" in values and values["folder_path"]:
                folder_id = self._path_to_file_id(service, values["folder_path"])
                if not folder_id:
                    return ErrorArtifact(f"Could not find folder: {values['folder_path']}")

            try:
                if len(artifacts) == 1:
                    self._save_to_drive(file_name, artifacts[0].value, folder_id)
                else:
                    for a in artifacts:
                        self._save_to_drive(f"{a.name}-{file_name}", a.value, folder_id)
    
                return InfoArtifact(f"saved successfully")
    
            except Exception as e:
                return ErrorArtifact(f"error saving file to Google Drive: {e}")
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to save content to a file",
        "schema": Schema(
            {
                Literal(
                    "path",
                    description="Destination file path on disk in the POSIX format. For example, 'foo/bar/baz.txt'"
                ): str,
                "content": str
            }
        )
    })
    def save_content_to_drive(self, params: dict) -> ErrorArtifact | InfoArtifact:
        content = params["values"]["content"]
        filename = params["values"]["path"]

        try:
            self._save_to_drive(filename, content)

            return InfoArtifact(f"saved successfully")
        except Exception as e:
            return ErrorArtifact(f"error saving file to Google Drive: {e}")

    def _save_to_drive(self, filename: str, value: any, parent_folder_id=None) -> InfoArtifact | ErrorArtifact:
        service = self._build_client(self.UPLOAD_FILE_SCOPES)
    
        if isinstance(value, str):
            value = value.encode()
    
        file_metadata = {"name": filename}
        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]
    
        media = MediaIoBaseUpload(BytesIO(value), mimetype="application/octet-stream", resumable=True)
    
        try:
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            return InfoArtifact(file.get("id"))
        except HttpError as error:
            return ErrorArtifact(f"An error occurred: {error}")

    @activity(config={
        "description": "Download a file from Google Drive based on a provided path",
        "schema": Schema({
            Literal("file_path",
                    description="Path of the Google Drive file (like 'MainFolder/Subfolder1/filename.ext') "
                                "that needs to be downloaded."): str
        })
    })
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
            return ErrorArtifact(f"error downloading file from Google Drive: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error downloading file due to malformed credentials")

    @activity(config={
        "description": "Search for a file on Google Drive based on name or content",
        "schema": Schema({
            Literal("search_mode",
                    description="Mode of search, either 'name' to search by file name or "
                                "'content' to search by file content."): str,
            Literal("file_name",
                    description="Name of the file to search for, used when search_mode is 'name'"): str,
            Optional("search_text",
                     description="Text to search for within files, used when search_mode is 'content'"): str,
            Optional("folder_path",
                     description="Path of the Google Drive folder (like 'MainFolder/Subfolder1') "
                                 "in which to restrict the search. If not provided, the search "
                                 "will span the entire Drive."): str
        })
    })
    def search_file(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]

        search_mode = values.get("search_mode", "name")

        try:
            service = self._build_client(self.LIST_FILES_SCOPES)

            folder_id = None
            if "folder_path" in values and values["folder_path"]:
                folder_id = self._path_to_file_id(service, values["folder_path"])
                if not folder_id:
                    return ErrorArtifact(f"Folder path {values['folder_path']} not found")

            if search_mode == "name":
                query = f"name='{values['file_name']}'"
            elif search_mode == "content":
                query = f"fullText contains '{values['search_text']}'"
            else:
                return ErrorArtifact(f"Invalid search mode: {search_mode}")

            query += " and trashed=false"

            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = service.files().list(q=query).execute()
            items = results.get('files', [])
            return ListArtifact(items)

        except HttpError as e:
            logging.error(e)
            return ErrorArtifact(f"error searching for file in Google Drive: {e}")
        except MalformedError:
            logging.error("MalformedError occurred")
            return ErrorArtifact("error searching for file due to malformed credentials")

