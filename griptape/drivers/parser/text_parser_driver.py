from __future__ import annotations

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.drivers import BaseParserDriver


@define
class TextParserDriver(BaseParserDriver[TextArtifact]):
    encoding: str = field(default="utf-8", kw_only=True)

    def try_parse(self, data: bytes, meta: dict) -> TextArtifact:
        return TextArtifact(data.decode(self.encoding), encoding=self.encoding)
