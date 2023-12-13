from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from griptape.utils import str_to_hash, import_optional_dependency
from griptape.drivers import BaseVectorStoreDriver
from attr import define, field

if TYPE_CHECKING:
    import pinecone


@define
class PineconeVectorStoreDriver(BaseVectorStoreDriver):
    api_key: str = field(kw_only=True)
    index_name: str = field(kw_only=True)
    environment: str = field(kw_only=True)
    project_name: str | None = field(default=None, kw_only=True)
    index: pinecone.Index = field(init=False)

    def __attrs_post_init__(self) -> None:
        pinecone = import_optional_dependency("pinecone")
        pinecone.init(api_key=self.api_key, environment=self.environment, project_name=self.project_name)

        self.index = pinecone.Index(self.index_name)

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs,
    ) -> str:
        vector_id = vector_id if vector_id else str_to_hash(str(vector))

        params = {"namespace": namespace} | kwargs

        self.index.upsert([(vector_id, vector, meta)], **params)

        return vector_id

    def load_entry(self, vector_id: str, namespace: str | None = None) -> BaseVectorStoreDriver.Entry | None:
        result = self.index.fetch(ids=[vector_id], namespace=namespace).to_dict()
        vectors = list(result["vectors"].values())

        if len(vectors) > 0:
            vector = vectors[0]

            return BaseVectorStoreDriver.Entry(
                id=vector["id"], meta=vector["metadata"], vector=vector["values"], namespace=result["namespace"]
            )
        else:
            return None

    def load_entries(self, namespace: str | None = None) -> list[BaseVectorStoreDriver.Entry]:
        # This is a hacky way to query up to 10,000 values from Pinecone. Waiting on an official API for fetching
        # all values from a namespace:
        # https://community.pinecone.io/t/is-there-a-way-to-query-all-the-vectors-and-or-metadata-from-a-namespace/797/5

        results = self.index.query(
            self.embedding_driver.embed_string(""), top_k=10000, include_metadata=True, namespace=namespace
        )

        return [
            BaseVectorStoreDriver.Entry(
                id=r["id"], vector=r["values"], meta=r["metadata"], namespace=results["namespace"]
            )
            for r in results["matches"]
        ]

    def query(
        self,
        query: str,
        count: int | None = None,
        namespace: str | None = None,
        include_vectors: bool = False,
        # PineconeVectorStorageDriver-specific params:
        include_metadata=True,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        vector = self.embedding_driver.embed_string(query)

        params = {
            "top_k": count if count else BaseVectorStoreDriver.DEFAULT_QUERY_COUNT,
            "namespace": namespace,
            "include_values": include_vectors,
            "include_metadata": include_metadata,
        } | kwargs

        results = self.index.query(vector, **params)

        return [
            BaseVectorStoreDriver.QueryResult(
                id=r["id"], vector=r["values"], score=r["score"], meta=r["metadata"], namespace=results["namespace"]
            )
            for r in results["matches"]
        ]

    def create_index(self, name: str, **kwargs) -> None:
        params = {"name": name, "dimension": self.embedding_driver.dimensions} | kwargs

        pinecone = import_optional_dependency("pinecone")
        pinecone.create_index(**params)
