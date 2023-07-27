from typing import Optional
from pymongo import MongoClient
from attr import define, field
from griptape.drivers import BaseVectorStoreDriver

@define
class MongoDbAtlasVectorStoreDriver(BaseVectorStoreDriver):
    connection_string: str = field(kw_only=True)
    database_name: str = field(kw_only=True)
    collection_name: str = field(kw_only=True)

    def _get_mongo_client(self) -> MongoClient:
        return MongoClient(self.connection_string)

    def _get_collection(self) -> any:
        mongo_client = self._get_mongo_client()
        return mongo_client[self.database_name][self.collection_name]

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs
    ) -> str:
        collection = self._get_collection()
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
        collection = self._get_collection()
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
        collection = self._get_collection()
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
        **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        raise NotImplementedError("Vector search not supported in MongoDB")
