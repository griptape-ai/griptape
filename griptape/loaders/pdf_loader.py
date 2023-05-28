from pathlib import Path
from typing import Union, IO
from PyPDF2 import PdfReader
from attr import define
from griptape.artifacts import ListArtifact
from griptape.loaders import TextLoader


@define
class PdfLoader(TextLoader):
    def load(self, stream: Union[str, IO, Path]) -> ListArtifact:
        reader = PdfReader(stream)
        text = "".join([p.extract_text() for p in reader.pages])

        return self.text_to_list_artifact(text)
