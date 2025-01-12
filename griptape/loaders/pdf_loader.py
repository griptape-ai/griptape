from __future__ import annotations

from io import BytesIO
from typing import Optional

from attrs import define

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.loaders.base_file_loader import BaseFileLoader
from griptape.utils import import_optional_dependency


@define
class PdfLoader(BaseFileLoader):
    def try_parse(
        self,
        data: bytes,
        *,
        password: Optional[str] = None,
    ) -> ListArtifact:
        pypdf = import_optional_dependency("pypdf")
        reader = pypdf.PdfReader(BytesIO(data), strict=True, password=password)
        pages = [TextArtifact(p.extract_text()) for p in reader.pages]

        return ListArtifact(pages)
