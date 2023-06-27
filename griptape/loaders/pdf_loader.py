from pathlib import Path
from typing import Union, IO, Optional
from PyPDF2 import PdfReader
from attr import define, field, Factory
from griptape import utils
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
        return self._load_pdf(stream, password)

    def load_collection(
            self,
            streams: list[Union[str, IO, Path]],
            password: Optional[str] = None
    ) -> dict[str, list[TextArtifact]]:
        return utils.execute_futures_dict({
            utils.str_to_hash(s.decode()) if isinstance(s, bytes) else utils.str_to_hash(str(s)):
                self.futures_executor.submit(self._load_pdf, s, password)
            for s in streams
        })

    def _load_pdf(self, stream: Union[str, IO, Path], password: Optional[str]) -> list[TextArtifact]:
        reader = PdfReader(stream, password=password)

        return self.text_to_artifacts("".join([p.extract_text() for p in reader.pages]))
