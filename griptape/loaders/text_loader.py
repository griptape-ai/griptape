from concurrent import futures
from concurrent.futures import Future
from typing import Optional
from attr import field, define, Factory
from griptape.artifacts import TextArtifact
from griptape.chunkers import TextChunker
from griptape.drivers import BaseEmbeddingDriver
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
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    executor: futures.Executor = field(
        default=Factory(lambda: futures.ThreadPoolExecutor()),
        kw_only=True
    )

    def load(self, text: str) -> list[TextArtifact]:
        return self.text_to_artifacts(text)

    def load_collection(self, texts: dict[str, str]) -> dict[str, list[TextArtifact]]:
        with self.executor as executor:
            return self._execute_futures_dict({
                key: executor.submit(self.text_to_artifacts, text) for key, text in texts.items()
            })

    def text_to_artifacts(self, text: str) -> list[TextArtifact]:
        artifacts = []

        if self.chunker:
            chunks = self.chunker.chunk(text)
        else:
            chunks = [TextArtifact(text)]

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts

    def _execute_futures_dict(self, fs_dict: dict[str, Future[list[TextArtifact]]]) -> dict[str, list[TextArtifact]]:
        futures.wait(fs_dict.values(), timeout=None, return_when=futures.ALL_COMPLETED)

        return {key: future.result() for key, future in fs_dict.items()}
