from typing import Optional, Callable
from scipy import spatial
from griptape import utils
from griptape.drivers import BaseVectorDriver, BaseEmbeddingDriver, OpenAiEmbeddingDriver
from attr import define, field, Factory


@define
class MemoryVectorDriver(BaseVectorDriver):
    entries: dict[str, BaseVectorDriver.VectorEntry] = field(factory=dict, kw_only=True)
    relatedness_fn: Callable = field(
        default=lambda x, y: 1 - spatial.distance.cosine(x, y),
        kw_only=True
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: OpenAiEmbeddingDriver()),
        kw_only=True
    )

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))

        self.entries[self._namespaced_vector_id(vector_id, namespace)] = self.VectorEntry(
            id=vector_id,
            vector=vector,
            meta=meta,
            namespace=namespace
        )

        return vector_id

    def load_vector(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorDriver.VectorEntry]:
        return self.entries.get(self._namespaced_vector_id(vector_id, namespace), None)

    def load_vectors(self, namespace: Optional[str] = None) -> list[BaseVectorDriver.VectorEntry]:
        return [entry for key, entry in self.entries.items() if namespace is None or entry.namespace == namespace]

    def query(
            self,
            query: str,
            count: Optional[int] = None,
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            **kwargs
    ) -> list[BaseVectorDriver.QueryResult]:
        query_embedding = self.embedding_driver.embed_string(query)

        if namespace:
            entries = {k: v for (k, v) in self.entries.items() if k.startswith(f"{namespace}-")}
        else:
            entries = self.entries

        entries_and_relatednesses = [
            (entry, self.relatedness_fn(query_embedding, entry.vector)) for entry in entries.values()
        ]
        entries_and_relatednesses.sort(key=lambda x: x[1], reverse=True)

        return [
            BaseVectorDriver.QueryResult(
                vector=er[0].vector,
                score=er[1],
                meta=er[0].meta
            ) for er in entries_and_relatednesses
        ][:count]

    def _namespaced_vector_id(self, vector_id: str, namespace: Optional[str]):
        return vector_id if namespace is None else f"{namespace}-{vector_id}"
