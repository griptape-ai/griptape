from __future__ import annotations

from typing import Any, cast

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.loaders import BaseFileLoader


@define
class TextLoader(BaseFileLoader):
    encoding: str = field(default="utf-8", kw_only=True)

    def load(self, source: Any, *args, **kwargs) -> TextArtifact:
        return cast(TextArtifact, super().load(source, *args, **kwargs))

    def parse(self, source: str | bytes, *args, **kwargs) -> TextArtifact:
        if isinstance(source, str):
            return TextArtifact(source, encoding=self.encoding)
        else:
            return TextArtifact(source.decode(self.encoding), encoding=self.encoding)
