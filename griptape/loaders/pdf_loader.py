from __future__ import annotations

from io import BytesIO
from typing import Optional, Union, cast

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.chunkers import PdfChunker
from griptape.loaders import BaseTextLoader
from griptape.utils import import_optional_dependency


@define
class PdfLoader(BaseTextLoader):
    chunker: PdfChunker = field(
        default=Factory(lambda self: PdfChunker(tokenizer=self.tokenizer, max_tokens=self.max_tokens), takes_self=True),
        kw_only=True,
    )
    encoding: None = field(default=None, kw_only=True)

    def load(
        self,
        source: bytes,
        password: Optional[str] = None,
        *args,
        **kwargs,
    ) -> ErrorArtifact | list[TextArtifact]:
        pypdf = import_optional_dependency("pypdf")
        reader = pypdf.PdfReader(BytesIO(source), strict=True, password=password)
        return self._text_to_artifacts("\n".join([p.extract_text() for p in reader.pages]))

    def load_collection(self, sources: list[bytes], *args, **kwargs) -> dict[str, ErrorArtifact | list[TextArtifact]]:
        return cast(
            dict[str, Union[ErrorArtifact, list[TextArtifact]]],
            super().load_collection(sources, *args, **kwargs),
        )
