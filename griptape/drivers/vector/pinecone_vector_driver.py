from typing import Optional
from griptape import utils
from griptape.drivers import BaseVectorDriver
import pinecone
from attr import define, field


@define
class PineconeVectorDriver(BaseVectorDriver):
    api_key: str = field(kw_only=True)
    index_name: str = field(kw_only=True)
    environment: str = field(kw_only=True)
    project_name: Optional[str] = field(default=None, kw_only=True)
    index: pinecone.Index = field(init=False)

    def __attrs_post_init__(self):
        pinecone.init(
            api_key=self.api_key,
            environment=self.environment,
            project_name=self.project_name
        )

        self.index = pinecone.Index(self.index_name)

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))

        params = {
            "namespace": namespace
        } | kwargs

        self.index.upsert([(vector_id, vector, meta)], **params)

        return vector_id

    def query(
            self,
            query: str,
            count: Optional[int] = None,
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            # PineconeVectorStorageDriver-specific params:
            include_metadata=True,
            **kwargs
    ) -> list[BaseVectorDriver.QueryResult]:
        vector = self.embedding_driver.embed_string(query)

        params = {
            "top_k": count if count else BaseVectorDriver.DEFAULT_QUERY_COUNT,
            "namespace": namespace,
            "include_values": include_vectors,
            "include_metadata": include_metadata
        } | kwargs

        results = self.index.query(vector, **params)

        return [
            BaseVectorDriver.QueryResult(
                vector=r["values"],
                score=r["score"],
                meta=r["metadata"],
                namespace=results["namespace"]
            )
            for r in results["matches"]
        ]

    def create_index(self, name: str, **kwargs) -> None:
        params = {
            "name": name,
            "dimension": self.embedding_driver.dimensions
        } | kwargs

        pinecone.create_index(**params)
