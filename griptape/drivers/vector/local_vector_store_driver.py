from typing import Optional, Callable
from numpy import dot
from numpy.linalg import norm
from griptape import utils
from griptape.drivers import BaseVectorStoreDriver
from attr import define, field


@define
class LocalVectorStoreDriver(BaseVectorStoreDriver):
    entries: dict[str, BaseVectorStoreDriver.Entry] = field(factory=dict, kw_only=True)
    relatedness_fn: Callable = field(default=lambda x, y: dot(x, y) / (norm(x) * norm(y)), kw_only=True)

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str:
        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))

        self.entries[self._namespaced_vector_id(vector_id, namespace)] = self.Entry(
            id=vector_id, vector=vector, meta=meta, namespace=namespace
        )

        return vector_id

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        return self.entries.get(self._namespaced_vector_id(vector_id, namespace), None)

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        return [entry for key, entry in self.entries.items() if namespace is None or entry.namespace == namespace]

    def query(
        self,
        query: str,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        query_embedding = self.embedding_driver.embed_string(query)

        if namespace:
            entries = {k: v for (k, v) in self.entries.items() if k.startswith(f"{namespace}-")}
        else:
            entries = self.entries

        entries_and_relatednesses = [
            (entry, self.relatedness_fn(query_embedding, entry.vector)) for entry in entries.values()
        ]
        entries_and_relatednesses.sort(key=lambda x: x[1], reverse=True)

        result = [
            BaseVectorStoreDriver.QueryResult(id=er[0].id, vector=er[0].vector, score=er[1], meta=er[0].meta)
            for er in entries_and_relatednesses
        ][:count]

        if include_vectors:
            return result
        else:
            return [
                BaseVectorStoreDriver.QueryResult(id=r.id, vector=[], score=r.score, meta=r.meta, namespace=r.namespace)
                for r in result
            ]

    def _namespaced_vector_id(self, vector_id: str, namespace: Optional[str]):
        return vector_id if namespace is None else f"{namespace}-{vector_id}"
