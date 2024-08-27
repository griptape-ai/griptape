from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.drivers import BaseFileManagerDriver, LocalFileManagerDriver
from griptape.loaders import BaseLoader

if TYPE_CHECKING:
    from os import PathLike


@define
class BaseFileLoader(BaseLoader, ABC):
    file_manager_driver: BaseFileManagerDriver = field(
        default=Factory(lambda: LocalFileManagerDriver(workdir=None)),
        kw_only=True,
    )
    encoding: str = field(default="utf-8", kw_only=True)

    def fetch(self, source: str | PathLike, *args, **kwargs) -> str | bytes:
        return self.file_manager_driver.load_file(str(source), *args, **kwargs).value
