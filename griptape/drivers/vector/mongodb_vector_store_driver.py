from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from attr import define, field, Factory
from griptape.drivers import BaseVectorStoreDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from pymongo import MongoClient, Collection


@define
class MongoDbAtlasVectorStoreDriver(BaseVectorStoreDriver):
    """A Vector Store Driver for MongoDb Atlas.

    Attributes:
        connection_string: The connection string for the MongoDb Atlas cluster.
        database_name: The name of the database to use.
        collection_name: The name of the collection to use.
        client: An optional MongoDb client to use. Defaults to a new client using the connection string.
    """

    connection_string: str = field(kw_only=True)
    database_name: str = field(kw_only=True)
    collection_name: str = field(kw_only=True)
    client: MongoClient | None = field(
        default=Factory(
            lambda self: import_optional_dependency("pymongo").MongoClient(self.connection_string), takes_self=True
        )
    )

    def get_collection(self) -> Collection:
        """Returns the MongoDB Collection instance for the specified database and collection name."""
        return self.client[self.database_name][self.collection_name]

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs,
    ) -> str:
        """Inserts or updates a vector in the collection.

        If a vector with the given vector ID already exists, it is updated; otherwise, a new vector is inserted.
        """
        collection = self.get_collection()

        if vector_id is None:
            result = collection.insert_one({"vector": vector, "namespace": namespace, "meta": meta})
            vector_id = str(result.inserted_id)
        else:
            collection.replace_one(
                {"_id": vector_id}, {"vector": vector, "namespace": namespace, "meta": meta}, upsert=True
            )
        return vector_id

    def load_entry(self, vector_id: str, namespace: str | None = None) -> BaseVectorStoreDriver.Entry | None:
        """Loads a document entry from the MongoDB collection based on the vector ID.

        Returns:
            The loaded Entry if found; otherwise, None is returned.
        """
        collection = self.get_collection()
        doc = collection.find_one({"_id": vector_id})
        if doc is None:
            return None
        return BaseVectorStoreDriver.Entry(
            id=str(doc["_id"]), vector=doc["vector"], namespace=doc["namespace"], meta=doc["meta"]
        )

    def load_entries(self, namespace: str | None = None) -> list[BaseVectorStoreDriver.Entry]:
        """Loads all document entries from the MongoDB collection.

        Entries can optionally be filtered by namespace.
        """
        collection = self.get_collection()
        if namespace is None:
            cursor = collection.find()
        else:
            cursor = collection.find({"namespace": namespace})

        for doc in cursor:
            yield BaseVectorStoreDriver.Entry(
                id=str(doc["_id"]), vector=doc["vector"], namespace=doc["namespace"], meta=doc["meta"]
            )

    def query(
        self,
        query: str,
        count: int | None = None,
        namespace: str | None = None,
        include_vectors: bool = False,
        offset: int | None = 0,
        index: str | None = None,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """Queries the MongoDB collection for documents that match the provided query string.

        Results can be customized based on parameters like count, namespace, inclusion of vectors, offset, and index.
        """
        collection = self.get_collection()

        # Using the embedding driver to convert the query string into a vector
        vector = self.embedding_driver.embed_string(query)

        knn_k = count if count else 10
        pipeline = [
            {"$search": {"knnBeta": {"vector": vector, "path": "vector", "k": knn_k + offset}}},
            {
                "$project": {
                    "_id": 1,
                    "vector": 1,
                    "namespace": 1,
                    "meta": 1,
                    "score": {"$meta": "searchScore"},  # Include the score in the projection
                }
            },
            {"$skip": offset},
            {"$limit": knn_k},
        ]

        if index:
            pipeline[0]["$search"]["index"] = index

        results = [
            BaseVectorStoreDriver.QueryResult(
                id=str(doc["_id"]),
                vector=doc["vector"] if include_vectors else None,
                score=doc["score"],  # Include the score in the result
                meta=doc["meta"],
                namespace=namespace,
            )
            for doc in list(collection.aggregate(pipeline))
        ]

        return results
