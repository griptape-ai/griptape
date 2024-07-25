from __future__ import annotations

import os
from pathlib import Path

from attrs import Attribute, Factory, define, field

from .base_file_manager_driver import BaseFileManagerDriver


@define
class LocalFileManagerDriver(BaseFileManagerDriver):
    """LocalFileManagerDriver can be used to list, load, and save files on the local file system.

    Attributes:
        workdir: The absolute working directory. List, load, and save operations will be performed relative to this directory.
    """

    workdir: str = field(default=Factory(lambda: os.getcwd()), kw_only=True)

    @workdir.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_workdir(self, _: Attribute, workdir: str) -> None:
        if not Path(workdir).is_absolute():
            raise ValueError("Workdir must be an absolute path")

    def try_list_files(self, path: str) -> list[str]:
        full_path = self._full_path(path)
        return os.listdir(full_path)

    def try_load_file(self, path: str) -> bytes:
        full_path = self._full_path(path)
        if self._is_dir(full_path):
            raise IsADirectoryError
        return Path(full_path).read_bytes()

    def try_save_file(self, path: str, value: bytes) -> None:
        full_path = self._full_path(path)
        if self._is_dir(full_path):
            raise IsADirectoryError
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        Path(full_path).write_bytes(value)

    def _full_path(self, path: str) -> str:
        path = path.lstrip("/")
        full_path = os.path.join(self.workdir, path)
        # Need to keep the trailing slash if it was there,
        # because it means the path is a directory.
        ended_with_slash = path.endswith("/")
        full_path = os.path.normpath(full_path)
        if ended_with_slash:
            full_path = full_path.rstrip("/") + "/"
        return full_path

    def _is_dir(self, full_path: str) -> bool:
        return full_path.endswith("/") or Path(full_path).is_dir()
