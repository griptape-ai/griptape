from __future__ import annotations
import os
from pathlib import Path
from attr import define, field, Factory
from .base_file_manager_driver import BaseFileManagerDriver


@define
class LocalFileManagerDriver(BaseFileManagerDriver):
    """
    LocalFileManagerDriver can be used to list, load, and save files on the local file system.

    Attributes:
        workdir: The absolute working directory. List, load, and save operations will be performed relative to this directory.
    """

    workdir: str = field(default=Factory(lambda: os.getcwd()), kw_only=True)

    @workdir.validator  # pyright: ignore
    def validate_workdir(self, _, workdir: str) -> None:
        if not Path(workdir).is_absolute():
            raise ValueError("Workdir must be an absolute path")

    def try_list_files(self, path: str) -> list[str]:
        full_path = self._full_path(path)
        return os.listdir(full_path)

    def try_load_file(self, path: str) -> bytes:
        full_path = self._full_path(path)
        with open(full_path, "rb") as file:
            return file.read()

    def try_save_file(self, path: str, value: bytes):
        full_path = self._full_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as file:
            file.write(value)

    def _full_path(self, path: str) -> Path:
        path = path.lstrip("/")
        return Path(os.path.normpath(os.path.join(self.workdir, path)))
