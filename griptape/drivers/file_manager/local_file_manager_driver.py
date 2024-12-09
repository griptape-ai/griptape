from __future__ import annotations

import os
from pathlib import Path

from attrs import Factory, define, field

from .base_file_manager_driver import BaseFileManagerDriver


@define
class LocalFileManagerDriver(BaseFileManagerDriver):
    """LocalFileManagerDriver can be used to list, load, and save files on the local file system.

    Attributes:
        workdir: The working directory as an absolute path. List, load, and save operations will be performed relative to this directory.
                 Defaults to the current working directory.
                 Setting this to None will disable the working directory and all paths will be treated as absolute paths.
    """

    _workdir: str = field(default=Factory(lambda: os.getcwd()), kw_only=True, alias="workdir")

    @property
    def workdir(self) -> str:
        if os.path.isabs(self._workdir):
            return self._workdir
        else:
            return os.path.join(os.getcwd(), self._workdir)

    @workdir.setter
    def workdir(self, value: str) -> None:
        self._workdir = value

    def try_list_files(self, path: str) -> list[str]:
        full_path = self._full_path(path)
        return os.listdir(full_path)

    def try_load_file(self, path: str) -> bytes:
        full_path = self._full_path(path)
        if self._is_dir(full_path):
            raise IsADirectoryError
        return Path(full_path).read_bytes()

    def try_save_file(self, path: str, value: bytes) -> str:
        full_path = self._full_path(path)
        if self._is_dir(full_path):
            raise IsADirectoryError
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        Path(full_path).write_bytes(value)
        return full_path

    def _full_path(self, path: str) -> str:
        full_path = path if os.path.isabs(path) else os.path.join(self.workdir, path.lstrip("/"))
        # Need to keep the trailing slash if it was there,
        # because it means the path is a directory.
        ended_with_sep = path.endswith("/")
        full_path = os.path.normpath(full_path)
        if ended_with_sep:
            full_path = full_path.rstrip("/") + "/"
        return full_path

    def _is_dir(self, full_path: str) -> bool:
        return full_path.endswith("/") or Path(full_path).is_dir()
