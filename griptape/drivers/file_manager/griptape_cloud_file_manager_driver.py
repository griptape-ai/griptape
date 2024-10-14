from __future__ import annotations

import os
import uuid
from typing import Optional
from urllib.parse import urljoin

import requests
from attrs import Attribute, Factory, define, field
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobClient

from .base_file_manager_driver import BaseFileManagerDriver


@define
class GriptapeCloudFileManagerDriver(BaseFileManagerDriver):
    """GriptapeCloudFileManagerDriver can be used to list, load, and save files as Assets in Griptape Cloud Buckets.

    Attributes:
        bucket_id: The ID of the Bucket to list, load, and save Assets in. If not provided, the driver will attempt to
            retrieve the ID from the environment variable `GT_CLOUD_BUCKET_ID`. If that is not set, a new Bucket will be
            created.
        bucket_name: The name of the new Bucket to be created if `bucket_id` is not set.
        workdir: The absolute working directory (must start and end with "/"). List, load, and save
            operations will be performed relative to this directory.
        base_url: The base URL of the Griptape Cloud API. Defaults to the value of the environment variable
            `GT_CLOUD_BASE_URL` or `https://cloud.griptape.ai`.
        api_key: The API key to use for authenticating with the Griptape Cloud API. If not provided, the driver will
            attempt to retrieve the API key from the environment variable `GT_CLOUD_API_KEY`.

    Raises:
        ValueError: If `api_key` is not provided or if `workdir` does not start with "/"".
    """

    bucket_id: Optional[str] = field(default=Factory(lambda: os.getenv("GT_CLOUD_BUCKET_ID")), kw_only=True)
    bucket_name: Optional[str] = field(default=None, kw_only=True)
    workdir: str = field(default="/", kw_only=True)
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: Optional[str] = field(default=Factory(lambda: os.getenv("GT_CLOUD_API_KEY")))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        init=False,
    )

    @workdir.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_workdir(self, _: Attribute, workdir: str) -> None:
        if not workdir.startswith("/"):
            raise ValueError(f"{self.__class__.__name__} requires Workdir to be an absolute path")

    @api_key.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_api_key(self, _: Attribute, value: Optional[str]) -> str:
        if value is None:
            raise ValueError(f"{self.__class__.__name__} requires an API key")
        return value

    def __attrs_post_init__(self) -> None:
        if self.bucket_id and self.bucket_name:
            raise ValueError("Only one of 'bucket_id' or 'bucket_name' may be provided, not both.")
        if self.bucket_id:
            try:
                self._call_api("get", f"/buckets/{self.bucket_id}").json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    raise ValueError(f"No Bucket found with ID: {self.bucket_id}") from e
                raise ValueError(f"Unexpected error when retrieving Bucket with ID: {self.bucket_id}") from e
        elif self.bucket_name:
            data = {"name": uuid.uuid4().hex} if self.bucket_name is None else {"name": self.bucket_name}
            post_bucket_response = self._call_api("post", f"/buckets{self.bucket_id}", data).json()
            self.bucket_id = post_bucket_response["bucket_id"]
        else:
            raise ValueError("Either 'bucket_id' or 'bucket_name' must be provided.")

    def try_list_files(self, path: str) -> list[str]:
        full_key = self._to_full_key(path)

        if not self._is_a_directory(full_key):
            raise NotADirectoryError

        data = {"filter": full_key}
        # TODO: Pagination
        list_assets_response = self._call_api(
            "list", f"/buckets/{self.bucket_id}/assets/{full_key}", data, raise_for_status=False
        ).json()

        return [asset["name"] for asset in list_assets_response.get("assets", [])]

    def try_load_file(self, path: str) -> bytes:
        full_key = self._to_full_key(path)

        if self._is_a_directory(full_key):
            raise IsADirectoryError

        try:
            blob_client = self._get_blob_client(full_key=full_key)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise FileNotFoundError from e
            raise e

        try:
            return blob_client.download_blob().readall()
        except ResourceNotFoundError as e:
            raise FileNotFoundError from e

    def try_save_file(self, path: str, value: bytes) -> None:
        full_key = self._to_full_key(path)

        if self._is_a_directory(full_key):
            raise IsADirectoryError

        blob_client = self._get_blob_client(full_key=full_key)

        blob_client.upload_blob(data=value, overwrite=True)

    def _get_url(self, path: str) -> str:
        path = path.lstrip("/")
        return urljoin(self.base_url, f"/api/{path}")

    def _call_api(
        self, method: str, path: str, json: Optional[dict] = None, *, raise_for_status: bool = True
    ) -> requests.Response:
        res = requests.request(method, self._get_url(path), json=json, headers=self.headers)
        if raise_for_status:
            res.raise_for_status()
        return res

    def _get_blob_client(self, full_key: str) -> BlobClient:
        url_response = self._call_api(
            method="post", path=f"/buckets/{self.bucket_id}/assets/{full_key}/url", raise_for_status=True
        ).json()
        sas_url = url_response["url"]
        return BlobClient.from_blob_url(blob_url=sas_url)

    def _is_a_directory(self, path: str) -> bool:
        return path == "" or path.endswith("/")

    def _to_full_key(self, path: str) -> str:
        path = path.lstrip("/")
        full_key = f"{self.workdir}/{path}"
        return full_key.lstrip("/")
