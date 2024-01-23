from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.drivers import BaseVectorStoreDriver, MongoDbAtlasVectorStoreDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from pymongo import MongoClient
    from pymongo.collection import Collection


@define
class AzureMongoDbVectorStoreDriver(MongoDbAtlasVectorStoreDriver):
    """A Vector Store Driver for CosmosDB with MongoDB vCore API."""

    def query(
        self,
        query: str,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        offset: Optional[int] = None,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """Queries the MongoDB collection for documents that match the provided query string.

        Results can be customized based on parameters like count, namespace, inclusion of vectors, offset, and index.
        """
        collection = self.get_collection()

        # Using the embedding driver to convert the query string into a vector
        vector = self.embedding_driver.embed_string(query)

        count = count if count else BaseVectorStoreDriver.DEFAULT_QUERY_COUNT
        offset = offset if offset else 0

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
                }
            }
        )

        if namespace:
            pipeline.append({"$match": {"namespace": namespace}})

        pipeline.append({"$project": {"similarityScore": {"$meta": "searchScore"}, "document": "$$ROOT"}})

        return [
            BaseVectorStoreDriver.QueryResult(
                id=str(doc["_id"]),
                vector=doc[self.vector_path] if include_vectors else [],
                score=doc["similarityScore"],
                meta=doc["document"]["meta"],
                namespace=namespace,
            )
            for doc in collection.aggregate(pipeline)
        ]
