from __future__ import annotations
from abc import ABC, abstractmethod
from concurrent import futures
from dataclasses import dataclass
from attr import define, field, Factory
from typing import Optional
from griptape import utils
from griptape.mixins import SerializableMixin
from griptape.artifacts import TextArtifact
from griptape.drivers import BaseEmbeddingDriver


@define
class BaseVectorStoreDriver(SerializableMixin, ABC):
    DEFAULT_QUERY_COUNT = 5

    @dataclass
    class QueryResult:
        id: str
        vector: list[float]
        score: float
        meta: dict | None = None
        namespace: str | None = None

    @dataclass
    class Entry:
        id: str
        vector: list[float]
        meta: dict | None = None
        namespace: str | None = None

    embedding_driver: BaseEmbeddingDriver = field(kw_only=True, metadata={"serialize": True})
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)

    def upsert_text_artifacts(
        self, artifacts: dict[str, list[TextArtifact]], meta: dict | None = None, **kwargs
    ) -> None:
        utils.execute_futures_dict(
            {
                namespace: self.futures_executor.submit(self.upsert_text_artifact, a, namespace, meta, **kwargs)
                for namespace, artifact_list in artifacts.items()
                for a in artifact_list
            }
        )

    def upsert_text_artifact(
        self, artifact: TextArtifact, namespace: str | None = None, meta: dict | None = None, **kwargs
    ) -> str:
        if not meta:
            meta = {}

        meta["artifact"] = artifact.to_json()

        if artifact.embedding:
            vector = artifact.embedding
        else:
            vector = artifact.generate_embedding(self.embedding_driver)

        return self.upsert_vector(vector, vector_id=artifact.id, namespace=namespace, meta=meta, **kwargs)

    def upsert_text(
        self,
        string: str,
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs,
    ) -> str:
        return self.upsert_vector(
            self.embedding_driver.embed_string(string),
            vector_id=vector_id,
            namespace=namespace,
            meta=meta if meta else {},
            **kwargs,
        )

    @abstractmethod
    def upsert_vector(
        self,
        vector: list[float],
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs,
    ) -> str:
        ...

    @abstractmethod
    def load_entry(self, vector_id: str, namespace: str | None = None) -> Entry | None:
        ...

    @abstractmethod
    def load_entries(self, namespace: str | None = None) -> list[Entry]:
        ...

    @abstractmethod
    def query(
        self,
        query: str,
        count: int | None = None,
        namespace: str | None = None,
        include_vectors: bool = False,
        **kwargs,
    ) -> list[QueryResult]:
        ...
