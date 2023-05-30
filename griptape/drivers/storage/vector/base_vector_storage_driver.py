from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BaseEmbeddingDriver, OpenAiEmbeddingDriver


@define
class BaseVectorStorageDriver(ABC):
    DEFAULT_QUERY_COUNT = 5

    @dataclass
    class QueryResult:
        vector: list[float]
        score: float
        meta: Optional[dict] = None
        namespace: Optional[str] = None

    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: OpenAiEmbeddingDriver()),
        kw_only=True
    )

    def insert_text_artifact(
            self,
            artifact: TextArtifact,
            vector_id: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        if not meta:
            meta = {}

        meta["artifact"] = artifact.to_dict()

        return self.insert_vector(
            artifact.generate_embedding(self.embedding_driver),
            vector_id=vector_id,
            meta=meta,
            **kwargs
        )

    def insert_text(
            self,
            string: str,
            vector_id: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        return self.insert_vector(
            self.embedding_driver.embed_string(string),
            vector_id=vector_id,
            meta=meta if meta else {},
            **kwargs
        )

    @abstractmethod
    def insert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        ...

    @abstractmethod
    def query(
            self,
            query: str,
            count: Optional[int] = None,
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            **kwargs
    ) -> list[QueryResult]:
        ...
