from pathlib import Path
from typing import Union, IO, Optional
from PyPDF2 import PdfReader
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.chunkers import PdfChunker
from griptape.loaders import TextLoader


@define
class PdfLoader(TextLoader):
    chunker: PdfChunker = field(
        default=Factory(
            lambda self: PdfChunker(
                tokenizer=self.tokenizer,
                max_tokens=self.max_tokens
            ),
            takes_self=True
        ),
        kw_only=True
    )

    def load(self, stream: Union[str, IO, Path], password: Optional[str] = None) -> list[TextArtifact]:
        reader = PdfReader(stream, password=password)
        text = "".join([p.extract_text() for p in reader.pages])

        return self.text_to_artifacts(text)
