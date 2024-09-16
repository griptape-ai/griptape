from __future__ import annotations

from io import BytesIO
from typing import Optional

from attrs import define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseParserDriver
from griptape.utils import import_optional_dependency


@define
class PyPdfParserDriver(BaseParserDriver[ListArtifact[TextArtifact]]):
    password: Optional[str] = field(default=None, kw_only=True)

    def try_parse(self, data: bytes, meta: dict) -> ListArtifact[TextArtifact]:
        pypdf = import_optional_dependency("pypdf")
        reader = pypdf.PdfReader(BytesIO(data), strict=True, password=self.password)
        pages = [TextArtifact(p.extract_text()) for p in reader.pages]

        return ListArtifact(pages)
