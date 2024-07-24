from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from concurrent import futures
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional

from attrs import Factory, define, field

from griptape import utils
from griptape.artifacts import BaseArtifact, ListArtifact, TextArtifact
from griptape.mixins import EventPublisherMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver


@define
class BaseVectorStoreDriver(EventPublisherMixin, SerializableMixin, ABC):
    DEFAULT_QUERY_COUNT = 5

    @dataclass
    class Entry:
        id: str
        vector: Optional[list[float]] = None
        score: Optional[float] = None
        meta: Optional[dict] = None
        namespace: Optional[str] = None

        @staticmethod
        def from_dict(data: dict[str, Any]) -> BaseVectorStoreDriver.Entry:
            return BaseVectorStoreDriver.Entry(**data)

        def to_artifact(self) -> BaseArtifact:
            return BaseArtifact.from_json(self.meta["artifact"])  # pyright: ignore[reportOptionalSubscript]

    embedding_driver: BaseEmbeddingDriver = field(kw_only=True, metadata={"serializable": True})
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()),
        kw_only=True,
    )

    def upsert_text_artifacts(
        self,
        artifacts: list[TextArtifact] | dict[str, list[TextArtifact]],
        *,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> None:
        with self.futures_executor_fn() as executor:
            if isinstance(artifacts, list):
                utils.execute_futures_list(
                    [
                        executor.submit(self.upsert_text_artifact, a, namespace=None, meta=meta, **kwargs)
                        for a in artifacts
                    ],
                )
            else:
                utils.execute_futures_dict(
                    {
                        namespace: executor.submit(
                            self.upsert_text_artifact, a, namespace=namespace, meta=meta, **kwargs
                        )
                        for namespace, artifact_list in artifacts.items()
                        for a in artifact_list
                    },
                )

    def upsert_text_artifact(
        self,
        artifact: TextArtifact,
        *,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        vector_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        meta = {} if meta is None else meta

        if vector_id is None:
            value = artifact.to_text() if artifact.reference is None else artifact.to_text() + str(artifact.reference)
            vector_id = self._get_default_vector_id(value)

        if self.does_entry_exist(vector_id, namespace=namespace):
            return vector_id
        else:
            meta["artifact"] = artifact.to_json()

            vector = artifact.embedding or artifact.generate_embedding(self.embedding_driver)

            if isinstance(vector, list):
                return self.upsert_vector(vector, vector_id=vector_id, namespace=namespace, meta=meta, **kwargs)
            else:
                raise ValueError("Vector must be an instance of 'list'.")

    def upsert_text(
        self,
        string: str,
        *,
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str:
        vector_id = self._get_default_vector_id(string) if vector_id is None else vector_id

        if self.does_entry_exist(vector_id, namespace=namespace):
            return vector_id
        else:
            return self.upsert_vector(
                self.embedding_driver.embed_string(string),
                vector_id=vector_id,
                namespace=namespace,
                meta=meta or {},
                **kwargs,
            )

    def does_entry_exist(self, vector_id: str, *, namespace: Optional[str] = None) -> bool:
        try:
            return self.load_entry(vector_id, namespace=namespace) is not None
        except Exception:
            return False

    def load_artifacts(self, *, namespace: Optional[str] = None) -> ListArtifact:
        result = self.load_entries(namespace=namespace)
        artifacts = [r.to_artifact() for r in result]

        return ListArtifact([a for a in artifacts if isinstance(a, TextArtifact)])

    @abstractmethod
    def delete_vector(self, vector_id: str) -> None: ...

    @abstractmethod
    def upsert_vector(
        self,
        vector: list[float],
        *,
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str: ...

    @abstractmethod
    def load_entry(self, vector_id: str, *, namespace: Optional[str] = None) -> Optional[Entry]: ...

    @abstractmethod
    def load_entries(self, *, namespace: Optional[str] = None) -> list[Entry]: ...

    @abstractmethod
    def query(
        self,
        query: str,
        *,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        **kwargs,
    ) -> list[Entry]: ...

    def _get_default_vector_id(self, value: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_OID, value))
