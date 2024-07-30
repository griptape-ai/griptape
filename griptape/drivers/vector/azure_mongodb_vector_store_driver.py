from __future__ import annotations

from typing import Optional

from attrs import define

from griptape.drivers import BaseVectorStoreDriver, MongoDbAtlasVectorStoreDriver


@define
class AzureMongoDbVectorStoreDriver(MongoDbAtlasVectorStoreDriver):
    """A Vector Store Driver for CosmosDB with MongoDB vCore API."""

    def query(
        self,
        query: str,
        *,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        offset: Optional[int] = None,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.Entry]:
        """Queries the MongoDB collection for documents that match the provided query string.

        Results can be customized based on parameters like count, namespace, inclusion of vectors, offset, and index.
        """
        collection = self.get_collection()

        # Using the embedding driver to convert the query string into a vector
        vector = self.embedding_driver.embed_string(query)

        count = count or BaseVectorStoreDriver.DEFAULT_QUERY_COUNT
        offset = offset or 0

        pipeline = []

        pipeline.append(
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": vector,
                        "path": self.vector_path,
                        "k": min(count * self.num_candidates_multiplier, self.MAX_NUM_CANDIDATES),
                    },
                    "returnStoredSource": True,
                },
            },
        )

        if namespace:
            pipeline.append({"$match": {"namespace": namespace}})

        pipeline.append({"$project": {"similarityScore": {"$meta": "searchScore"}, "document": "$$ROOT"}})

        return [
            BaseVectorStoreDriver.Entry(
                id=str(doc["_id"]),
                vector=doc[self.vector_path] if include_vectors else [],
                score=doc["similarityScore"],
                meta=doc["document"]["meta"],
                namespace=namespace,
            )
            for doc in collection.aggregate(pipeline)
        ]
