from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from concurrent import futures
from dataclasses import dataclass
from typing import Any, Callable, Optional

from attrs import Factory, define, field

from griptape import utils
from griptape.artifacts import BaseArtifact, ListArtifact
from griptape.mixins import SerializableMixin


@define
class BaseGraphStoreDriver(SerializableMixin, ABC):
    DEFAULT_QUERY_COUNT = 5

    @dataclass
    class Entry:
        id: str
        properties: Optional[dict] = None
        score: Optional[float] = None
        namespace: Optional[str] = None

        @staticmethod
        def from_dict(data: dict[str, Any]) -> BaseGraphStoreDriver.Entry:
            return BaseGraphStoreDriver.Entry(**data)

        def to_artifact(self) -> BaseArtifact:
            return BaseArtifact.from_json(self.properties["artifact"])  # pyright: ignore[reportOptionalSubscript]

    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()), kw_only=True
    )

    def upsert_artifacts(self, artifacts: dict[str, list[BaseArtifact]], meta: Optional[dict] = None, **kwargs) -> None:
        with self.futures_executor_fn() as executor:
            utils.execute_futures_dict(
                {
                    namespace: executor.submit(self.upsert_artifact, a, namespace, meta, **kwargs)
                    for namespace, artifact_list in artifacts.items()
                    for a in artifact_list
                }
            )

    def upsert_artifact(
        self,
        artifact: BaseArtifact,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        node_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        meta = {} if meta is None else meta
        node_id = self._get_default_node_id(artifact.to_text()) if node_id is None else node_id

        if self.does_entry_exist(node_id, namespace):
            return node_id
        else:
            meta["artifact"] = artifact.to_json()
            return self.upsert_node(node_id=node_id, namespace=namespace, meta=meta, **kwargs)

    def does_entry_exist(self, node_id: str, namespace: Optional[str] = None) -> bool:
        try:
            return self.load_entry(node_id, namespace) is not None
        except Exception:
            return False

    def load_artifacts(self, namespace: Optional[str] = None) -> ListArtifact:
        result = self.load_entries(namespace)
        artifacts = [r.to_artifact() for r in result]

        return ListArtifact([a for a in artifacts if isinstance(a, BaseArtifact)])

    @abstractmethod
    def delete_node(self, node_id: str) -> None: ...

    @abstractmethod
    def upsert_node(
        self,
        node_data: dict[str, Any],
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str: ...

    @abstractmethod
    def load_entry(self, node_id: str, namespace: Optional[str] = None) -> Optional[Entry]: ...

    @abstractmethod
    def load_entries(self, namespace: Optional[str] = None) -> list[Entry]: ...

    @abstractmethod
    def query(
        self,
        query: str,
        params: Optional[dict[str, Any]] = None,
        namespace: Optional[str] = None,
        **kwargs,
    ) -> Any: ...

    def _get_default_node_id(self, value: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_OID, value))
