from __future__ import annotations
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any
from attrs import define, field, Factory
from griptape.utils.import_utils import import_optional_dependency
from .base_file_manager_driver import BaseFileManagerDriver

if TYPE_CHECKING:
    import boto3


@define
class AmazonS3FileManagerDriver(BaseFileManagerDriver):
    """
    AmazonS3FileManagerDriver can be used to list, load, and save files in an Amazon S3 bucket.

    Attributes:
        session: The boto3 session to use for S3 operations.
        bucket: The name of the S3 bucket.
        workdir: The absolute working directory (must start with "/"). List, load, and save
            operations will be performed relative to this directory.
        s3_client: The S3 client to use for S3 operations.
    """

    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bucket: str = field(kw_only=True)
    workdir: str = field(default="/", kw_only=True)
    s3_client: Any = field(default=Factory(lambda self: self.session.client("s3"), takes_self=True), kw_only=True)

    @workdir.validator  # pyright: ignore
    def validate_workdir(self, _, workdir: str) -> None:
        if not Path(workdir).is_absolute():
            raise ValueError("Workdir must be an absolute path")

    def try_list_files(self, path: str) -> list[str]:
        full_key = self._to_dir_full_key(path)
        files_and_dirs = self._list_files_and_dirs(full_key)
        if len(files_and_dirs) == 0:
            if len(self._list_files_and_dirs(full_key.rstrip("/"), max_items=1)) > 0:
                raise NotADirectoryError
            else:
                raise FileNotFoundError
        return files_and_dirs

    def try_load_file(self, path: str) -> bytes:
        botocore = import_optional_dependency("botocore")
        full_key = self._to_full_key(path)

        if self._is_a_directory(full_key):
            raise IsADirectoryError

        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=full_key)
            return response["Body"].read()
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] in {"NoSuchKey", "404"}:
                raise FileNotFoundError from e
            else:
                raise e

    def try_save_file(self, path: str, value: bytes):
        full_key = self._to_full_key(path)
        if self._is_a_directory(full_key):
            raise IsADirectoryError
        self.s3_client.put_object(Bucket=self.bucket, Key=full_key, Body=value)

    def _to_full_key(self, path: str) -> str:
        path = path.lstrip("/")
        full_key = os.path.join(self.workdir, path)
        # Need to keep the trailing slash if it was there,
        # because it means the path is a directory.
        ended_with_slash = path.endswith("/")
        full_key = os.path.normpath(full_key)
        if ended_with_slash:
            full_key += "/"
        return full_key.lstrip("/")

    def _to_dir_full_key(self, path: str) -> str:
        full_key = self._to_full_key(path)
        # S3 "directories" always end with a slash, except for the root.
        if full_key != "" and not full_key.endswith("/"):
            full_key += "/"
        return full_key

    def _list_files_and_dirs(self, full_key: str, **kwargs) -> list[str]:
        max_items = kwargs.get("max_items")
        pagination_config = {}
        if max_items is not None:
            pagination_config["MaxItems"] = max_items

        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(
            Bucket=self.bucket, Prefix=full_key, Delimiter="/", PaginationConfig=pagination_config
        )
        files_and_dirs = []
        for page in pages:
            for obj in page.get("CommonPrefixes", []):
                prefix = obj.get("Prefix")
                dir = prefix[len(full_key) :].rstrip("/")
                files_and_dirs.append(dir)

            for obj in page.get("Contents", []):
                key = obj.get("Key")
                file = key[len(full_key) :]
                files_and_dirs.append(file)
        return files_and_dirs

    def _is_a_directory(self, full_key: str) -> bool:
        botocore = import_optional_dependency("botocore")
        if full_key == "" or full_key.endswith("/"):
            return True

        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=full_key)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] in {"NoSuchKey", "404"}:
                return len(self._list_files_and_dirs(full_key, max_items=1)) > 0
            else:
                raise e

        return False
