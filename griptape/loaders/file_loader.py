from __future__ import annotations

from os import PathLike
from typing import TypeVar, Union, cast

from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact
from griptape.artifacts.blob_artifact import BlobArtifact
from griptape.drivers import (
    AudioParserDriver,
    BaseFileManagerDriver,
    BaseParserDriver,
    CsvParserDriver,
    LocalFileManagerDriver,
    PillowParserDriver,
    PyPdfParserDriver,
    TextParserDriver,
)
from griptape.loaders import BaseLoader
from griptape.utils import get_mime_type

A = TypeVar("A", bound=BaseArtifact)


@define
class FileLoader(BaseLoader[Union[str, PathLike], bytes, A]):
    file_manager_driver: BaseFileManagerDriver = field(
        default=Factory(lambda: LocalFileManagerDriver(workdir=None)),
        kw_only=True,
    )
    parser_driver_map: dict[str, BaseParserDriver] = field(
        default=Factory(
            lambda: {
                "application/pdf": PyPdfParserDriver(),
                "text/csv": CsvParserDriver(),
                "text": TextParserDriver(),
                "image": PillowParserDriver(),
                "audio": AudioParserDriver(),
            }
        ),
        kw_only=True,
    )
    encoding: str = field(default="utf-8", kw_only=True)

    def fetch(self, source: str | PathLike) -> tuple[bytes, dict]:
        data = self.file_manager_driver.load_file(str(source)).value
        meta = {"mime_type": get_mime_type(str(source))}

        if isinstance(data, str):
            return data.encode(self.encoding), meta
        else:
            return data, meta

    def parse(self, data: bytes, meta: dict) -> A:
        mime_type = meta["mime_type"]

        driver = next((loader for key, loader in self.parser_driver_map.items() if mime_type.startswith(key)), None)

        artifact = BlobArtifact(data) if driver is None else driver.parse(data, meta)

        return cast(A, artifact)
