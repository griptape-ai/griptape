from typing import Optional
from pymongo import MongoClient
from attr import define, field, Factory
from pymongo.collection import Collection
from griptape.drivers import BaseVectorStoreDriver


@define
class MongoDbAtlasVectorStoreDriver(BaseVectorStoreDriver):
    connection_string: str = field(kw_only=True)
    database_name: str = field(kw_only=True)
    collection_name: str = field(kw_only=True)
    client: MongoClient = field(
        default=Factory(lambda self: MongoClient(self.connection_string), takes_self=True)
    )

    def get_collection(self) -> Collection:
        return self.client[self.database_name][self.collection_name]

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        collection = self.get_collection()

        if vector_id is None:
            result = collection.insert_one(
                {
                    "vector": vector,
                    "namespace": namespace,
                    "meta": meta,
                }
            )
            vector_id = str(result.inserted_id)
        else:
            collection.replace_one(
                {"_id": vector_id},
                {
                    "vector": vector,
                    "namespace": namespace,
                    "meta": meta,
                },
                upsert=True,
            )
        return vector_id

    def load_entry(
            self, vector_id: str, namespace: Optional[str] = None
    ) -> Optional[BaseVectorStoreDriver.Entry]:
        collection = self.get_collection()
        doc = collection.find_one({"_id": vector_id})
        if doc is None:
            return None
        return BaseVectorStoreDriver.Entry(
            id=str(doc["_id"]),
            vector=doc["vector"],
            namespace=doc["namespace"],
            meta=doc["meta"],
        )

    def load_entries(
            self, namespace: Optional[str] = None
    ) -> list[BaseVectorStoreDriver.Entry]:
        collection = self.get_collection()
        if namespace is None:
            cursor = collection.find()
        else:
            cursor = collection.find({"namespace": namespace})

        for doc in cursor:
            yield BaseVectorStoreDriver.Entry(
                id=str(doc["_id"]),
                vector=doc["vector"],
                namespace=doc["namespace"],
                meta=doc["meta"],
            )

    def query(
            self,
            query: str,
            count: Optional[int] = None,
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            offset: Optional[int] = 0,
            **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        collection = self.get_collection()

        # Using the embedding driver to convert the query string into a vector
        vector = self.embedding_driver.embed_string(query)
        print("Vector for query:", vector)

        knn_k = count if count else 10
        pipeline = [
            {
                "$search": {
                    "index": "knn",  # Use the name of the k-NN index you created
                    "knnBeta": {
                        "vector": vector,
                        "path": "vector",
                        "k": knn_k + offset
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "vector": 1,
                    "namespace": 1,
                    "meta": 1
                }
            },
            {"$skip": offset},
            {"$limit": knn_k}
        ]

        cursor = collection.aggregate(pipeline)
        #print("Pipeline:", pipeline)
        #print("Cursor:", list(cursor))
        list_cursor = list(cursor)
        for doc in list_cursor:
            print(doc)
        results = [
            BaseVectorStoreDriver.QueryResult(
                vector=doc["vector"] if include_vectors else None,
                score=None,  # Score is not directly provided by knnBeta
                meta=doc["meta"],
                namespace=namespace,  # Added namespace to QueryResult
            )
            for doc in list_cursor
        ]
        #print("In Driver results: ", results)
        return results
