from __future__ import annotations

import logging
import os
from typing import Optional
from urllib.parse import urljoin

import requests
from attrs import Attribute, Factory, define, field

from griptape.drivers import BaseFileManagerDriver

logger = logging.getLogger(__name__)


@define
class GriptapeCloudFileManagerDriver(BaseFileManagerDriver):
    """GriptapeCloudFileManagerDriver can be used to list, load, and save files as Assets in Griptape Cloud Buckets.

    Attributes:
        bucket_id: The ID of the Bucket to list, load, and save Assets in. If not provided, the driver will attempt to
            retrieve the ID from the environment variable `GT_CLOUD_BUCKET_ID`.
        workdir: The working directory. List, load, and save operations will be performed relative to this directory.
        base_url: The base URL of the Griptape Cloud API. Defaults to the value of the environment variable
            `GT_CLOUD_BASE_URL` or `https://cloud.griptape.ai`.
        api_key: The API key to use for authenticating with the Griptape Cloud API. If not provided, the driver will
            attempt to retrieve the API key from the environment variable `GT_CLOUD_API_KEY`.

    Raises:
        ValueError: If `api_key` is not provided, if `workdir` does not start with "/"", or invalid `bucket_id` and/or `bucket_name` value(s) are provided.
    """

    bucket_id: Optional[str] = field(default=Factory(lambda: os.getenv("GT_CLOUD_BUCKET_ID")), kw_only=True)
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        init=False,
    )
    _workdir: str = field(default="/", kw_only=True, alias="workdir")

    @property
    def workdir(self) -> str:
        if self._workdir.startswith("/"):
            return self._workdir
        else:
            return f"/{self._workdir}"

    @workdir.setter
    def workdir(self, value: str) -> None:
        self._workdir = value

    @bucket_id.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_bucket_id(self, _: Attribute, value: Optional[str]) -> str:
        if value is None:
            raise ValueError(f"{self.__class__.__name__} requires an Bucket ID")
        return value

    def __attrs_post_init__(self) -> None:
        try:
            self._call_api(method="get", path=f"/buckets/{self.bucket_id}").json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"No Bucket found with ID: {self.bucket_id}") from e
            raise ValueError(f"Unexpected error when retrieving Bucket with ID: {self.bucket_id}") from e

    def try_list_files(self, path: str, postfix: str = "") -> list[str]:
        full_key = self._to_full_key(path)

        data = {"prefix": full_key}
        if postfix:
            data["postfix"] = postfix
        list_assets_response = self._call_api(
            method="get", path=f"/buckets/{self.bucket_id}/assets", json=data, raise_for_status=False
        ).json()

        return [asset["name"] for asset in list_assets_response.get("assets", [])]

    def try_load_file(self, path: str) -> bytes:
        full_key = self._to_full_key(path)

        if self._is_a_directory(full_key):
            raise IsADirectoryError

        try:
            sas_url, headers = self._get_asset_url(full_key)
            response = requests.get(sas_url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise FileNotFoundError from e
            raise e

    def try_save_file(self, path: str, value: bytes) -> str:
        full_key = self._to_full_key(path)

        if self._is_a_directory(full_key):
            raise IsADirectoryError

        self._call_api(
            method="put",
            path=f"/buckets/{self.bucket_id}/assets",
            json={"name": full_key},
            raise_for_status=True,
        )

        sas_url, headers = self._get_asset_url(full_key)
        response = requests.put(sas_url, data=value, headers=headers)
        response.raise_for_status()

        return f"buckets/{self.bucket_id}/assets/{full_key}"

    def _get_asset_url(self, full_key: str) -> tuple[str, dict]:
        url_response = self._call_api(
            method="post", path=f"/buckets/{self.bucket_id}/asset-urls/{full_key}", raise_for_status=True
        ).json()
        return url_response["url"], url_response.get("headers", {})

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

    def _is_a_directory(self, path: str) -> bool:
        return path == "" or path.endswith("/")

    def _to_full_key(self, path: str) -> str:
        path = path.lstrip("/")
        full_key = f"{self.workdir}/{path}"
        return full_key.lstrip("/")
