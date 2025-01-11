from __future__ import annotations

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.loaders import BaseFileLoader


@define
class TextLoader(BaseFileLoader[TextArtifact]):
    encoding: str = field(default="utf-8", kw_only=True)

    def try_parse(self, data: str | bytes) -> TextArtifact:
        if isinstance(data, str):
            return TextArtifact(data, encoding=self.encoding)
        else:
            return TextArtifact(data.decode(self.encoding), encoding=self.encoding)
