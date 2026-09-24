from __future__ import annotations

import uuid
import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, overload

from attrs import define, field

from griptape import utils
from griptape.artifacts import BaseArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin
from griptape.mixins.serializable_mixin import SerializableMixin
from griptape.utils import with_contextvars

if TYPE_CHECKING:
    from collections.abc import Callable

    from griptape.drivers.embedding import BaseEmbeddingDriver


@define
class BaseVectorStoreDriver(SerializableMixin, FuturesExecutorMixin, ABC):
    DEFAULT_QUERY_COUNT = 5

    @define
    class Entry(SerializableMixin):
        id: str = field(metadata={"serializable": True})
        vector: list[float] | None = field(default=None, metadata={"serializable": True})
        score: float | None = field(default=None, metadata={"serializable": True})
        meta: dict | None = field(default=None, metadata={"serializable": True})
        namespace: str | None = field(default=None, metadata={"serializable": True})

        def to_artifact(self) -> BaseArtifact:
            return BaseArtifact.from_json(self.meta["artifact"])  # pyright: ignore[reportOptionalSubscript]

    embedding_driver: BaseEmbeddingDriver = field(kw_only=True, metadata={"serializable": True})

    def upsert_text_artifacts(
        self,
        artifacts: list[TextArtifact] | dict[str, list[TextArtifact]],
        *,
        meta: dict | None = None,
        **kwargs,
    ) -> list[str] | dict[str, list[str]]:
        warnings.warn(
            "`BaseVectorStoreDriver.upsert_text_artifacts` is deprecated and will be removed in a future release. `BaseVectorStoreDriver.upsert_collection` is a drop-in replacement.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.upsert_collection(artifacts, meta=meta, **kwargs)

    def upsert_text_artifact(
        self,
        artifact: TextArtifact,
        *,
        namespace: str | None = None,
        meta: dict | None = None,
        vector_id: str | None = None,
        **kwargs,
    ) -> str:
        warnings.warn(
            "`BaseVectorStoreDriver.upsert_text_artifacts` is deprecated and will be removed in a future release. `BaseVectorStoreDriver.upsert` is a drop-in replacement.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.upsert(artifact, namespace=namespace, meta=meta, vector_id=vector_id, **kwargs)

    def upsert_text(
        self,
        string: str,
        *,
        namespace: str | None = None,
        meta: dict | None = None,
        vector_id: str | None = None,
        **kwargs,
    ) -> str:
        warnings.warn(
            "`BaseVectorStoreDriver.upsert_text` is deprecated and will be removed in a future release. `BaseVectorStoreDriver.upsert` is a drop-in replacement.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.upsert(string, namespace=namespace, meta=meta, vector_id=vector_id, **kwargs)

    @overload
    def upsert_collection(
        self,
        artifacts: list[TextArtifact] | list[ImageArtifact],
        *,
        meta: dict | None = None,
        **kwargs,
    ) -> list[str]: ...

    @overload
    def upsert_collection(
        self,
        artifacts: dict[str, list[TextArtifact]] | dict[str, list[ImageArtifact]],
        *,
        meta: dict | None = None,
        **kwargs,
    ) -> dict[str, list[str]]: ...

    def upsert_collection(
        self,
        artifacts: list[TextArtifact]
        | list[ImageArtifact]
        | dict[str, list[TextArtifact]]
        | dict[str, list[ImageArtifact]],
        *,
        meta: dict | None = None,
        **kwargs,
    ):
        return self._execute_collection_operation(artifacts, self.upsert, meta=meta, **kwargs)

    def upsert(
        self,
        value: str | TextArtifact | ImageArtifact,
        *,
        namespace: str | None = None,
        meta: dict | None = None,
        vector_id: str | None = None,
        **kwargs,
    ) -> str:
        artifact = TextArtifact(value) if isinstance(value, str) else value

        meta = {} if meta is None else meta

        if vector_id is None:
            value = artifact.to_text() if artifact.reference is None else artifact.to_text() + str(artifact.reference)
            vector_id = self._get_default_vector_id(value)

        meta = {**meta, "artifact": artifact.to_json()}

        vector = self.embedding_driver.embed(artifact, vector_operation="upsert")

        return self.upsert_vector(vector, vector_id=vector_id, namespace=namespace, meta=meta, **kwargs)

    def insert(
        self,
        value: str | TextArtifact | ImageArtifact,
        *,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs: Any,
    ) -> str:
        """Insert a value into the vector store with a randomly generated ID.

        Args:
            value: The value to insert.
            namespace: An optional namespace for the value.
            meta: An optional dictionary of metadata for the value.
            kwargs: Additional keyword arguments to pass to the vector store driver.

        Returns:
            str: The generated vector ID.
        """
        return self.upsert(value, namespace=namespace, meta=meta, vector_id=str(uuid.uuid4()), **kwargs)

    @overload
    def insert_collection(
        self,
        artifacts: list[TextArtifact] | list[ImageArtifact],
        *,
        meta: dict | None = None,
        **kwargs,
    ) -> list[str]: ...

    @overload
    def insert_collection(
        self,
        artifacts: dict[str, list[TextArtifact]] | dict[str, list[ImageArtifact]],
        *,
        meta: dict | None = None,
        **kwargs,
    ) -> dict[str, list[str]]: ...

    def insert_collection(
        self,
        artifacts: list[TextArtifact]
        | list[ImageArtifact]
        | dict[str, list[TextArtifact]]
        | dict[str, list[ImageArtifact]],
        *,
        meta: dict | None = None,
        **kwargs: Any,
    ) -> list[str] | dict[str, list[str]]:
        """Insert a collection of artifacts into the vector store with randomly generated IDs.

        Args:
            artifacts: The artifacts to insert, optionally grouped by namespace.
            meta: An optional dictionary of metadata for the artifacts.
            kwargs: Additional keyword arguments to pass to the vector store driver.

        Returns:
            list[str] | dict[str, list[str]]: The generated vector IDs.
        """
        return self._execute_collection_operation(artifacts, self.insert, meta=meta, **kwargs)

    def _execute_collection_operation(
        self,
        artifacts: list[TextArtifact]
        | list[ImageArtifact]
        | dict[str, list[TextArtifact]]
        | dict[str, list[ImageArtifact]],
        operation: Callable[..., str],
        *,
        meta: dict | None = None,
        **kwargs,
    ) -> list[str] | dict[str, list[str]]:
        with self.create_futures_executor() as futures_executor:
            if isinstance(artifacts, list):
                return utils.execute_futures_list(
                    [
                        futures_executor.submit(with_contextvars(operation), a, namespace=None, meta=meta, **kwargs)
                        for a in artifacts
                    ],
                )
            futures_dict = {}

            for namespace, artifact_list in artifacts.items():
                for a in artifact_list:
                    if not futures_dict.get(namespace):
                        futures_dict[namespace] = []

                    futures_dict[namespace].append(
                        futures_executor.submit(
                            with_contextvars(operation), a, namespace=namespace, meta=meta, **kwargs
                        )
                    )

            return utils.execute_futures_list_dict(futures_dict)

    def does_entry_exist(self, vector_id: str, *, namespace: str | None = None) -> bool:
        try:
            return self.load_entry(vector_id, namespace=namespace) is not None
        except Exception:
            return False

    def load_artifacts(self, *, namespace: str | None = None) -> ListArtifact:
        result = self.load_entries(namespace=namespace)
        artifacts = [r.to_artifact() for r in result]

        return ListArtifact([a for a in artifacts if isinstance(a, TextArtifact)])

    @abstractmethod
    def delete_vector(self, vector_id: str) -> None:
        pass

    @abstractmethod
    def upsert_vector(
        self,
        vector: list[float],
        *,
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    def load_entry(self, vector_id: str, *, namespace: str | None = None) -> Entry | None:
        pass

    @abstractmethod
    def load_entries(self, *, namespace: str | None = None) -> list[Entry]:
        pass

    def query_vector(
        self,
        vector: list[float],
        *,
        count: int | None = None,
        namespace: str | None = None,
        include_vectors: bool = False,
        **kwargs,
    ) -> list[Entry]:
        # TODO: Mark as abstract method for griptape 2.0
        raise NotImplementedError(f"{self.__class__.__name__} does not support vector query.")

    def query(
        self,
        query: str | TextArtifact | ImageArtifact,
        *,
        count: int | None = None,
        namespace: str | None = None,
        include_vectors: bool = False,
        **kwargs,
    ) -> list[Entry]:
        try:
            vector = self.embedding_driver.embed(query, vector_operation="query")
        except ValueError as e:
            raise ValueError(
                "The Embedding Driver, %s, used by the Vector Store does not support embedding the %s type."
                "To resolve, provide an Embedding Driver that supports this type.",
                self.embedding_driver.__class__.__name__,
                type(query),
            ) from e
        return self.query_vector(vector, count=count, namespace=namespace, include_vectors=include_vectors, **kwargs)

    def _get_default_vector_id(self, value: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_OID, value))
