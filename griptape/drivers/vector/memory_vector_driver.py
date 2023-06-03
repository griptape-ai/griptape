from dataclasses import dataclass
from typing import Optional, Callable
from scipy import spatial
from griptape import utils
from griptape.drivers import BaseVectorDriver, BaseEmbeddingDriver, OpenAiEmbeddingDriver
from attr import define, field, Factory


@define
class MemoryVectorDriver(BaseVectorDriver):
    @dataclass
    class Entry:
        vector: list[float]
        meta: Optional[dict] = None

    entries: dict[str, Entry] = field(factory=dict, kw_only=True)
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
        vector_id = f"{namespace}-{vector_id}" if namespace else vector_id

        self.entries[vector_id] = self.Entry(vector, meta)

        return vector_id

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
