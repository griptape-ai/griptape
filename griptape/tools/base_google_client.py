from __future__ import annotations

from abc import ABC
from typing import Any, Optional

from attrs import define, field

from griptape.tools import BaseTool


@define
class BaseGoogleClient(BaseTool, ABC):
    DRIVE_FILE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    DRIVE_AUTH_SCOPES = ["https://www.googleapis.com/auth/drive"]

    service_account_credentials: dict = field(kw_only=True)

    def _build_client(self, scopes: list[str], service_name: str, version: str, owner_email: str) -> Any:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_info(
            self.service_account_credentials,
            scopes=scopes,
        )

        return build(serviceName=service_name, version=version, credentials=credentials.with_subject(owner_email))

    def _convert_path_to_file_id(self, service: Any, path: str) -> Optional[str]:
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
