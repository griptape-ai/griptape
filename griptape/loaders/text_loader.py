from pathlib import Path
from typing import Union
from attr import field, define, Factory
from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.chunkers import TextChunker
from griptape.loaders import BaseLoader
from griptape.tokenizers import TiktokenTokenizer


@define
class TextLoader(BaseLoader):
    MAX_TOKEN_RATIO = 0.5

    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda: TiktokenTokenizer()),
        kw_only=True
    )
    max_tokens: int = field(
        default=Factory(lambda self: round(self.tokenizer.max_tokens * self.MAX_TOKEN_RATIO), takes_self=True),
        kw_only=True
    )
    chunker: TextChunker = field(
        default=Factory(
            lambda self: TextChunker(
                tokenizer=self.tokenizer,
                max_tokens=self.max_tokens
            ),
            takes_self=True
        ),
        kw_only=True
    )

    def load(self, text: Union[str, Path]) -> list[TextArtifact]:
        return self.text_to_artifacts(text)

    def load_collection(self, texts: list[Union[str, Path]]) -> dict[str, list[TextArtifact]]:
        return utils.execute_futures_dict({
            utils.str_to_hash(str(text)): self.futures_executor.submit(self.text_to_artifacts, text)
            for text in texts
        })

    def text_to_artifacts(self, text: Union[str, Path]) -> list[TextArtifact]:
        artifacts = []

        if isinstance(text, Path):
            with open(text, "r") as file:
                body = file.read()
        else:
            body = text

        if self.chunker:
            chunks = self.chunker.chunk(body)
        else:
            chunks = [TextArtifact(body)]

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts
