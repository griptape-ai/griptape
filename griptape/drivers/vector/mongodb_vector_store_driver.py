from typing import Optional
from pymongo import MongoClient
from attr import define, field, Factory
from bson import ObjectId  # needed for ObjectId to str conversion
from griptape.drivers import BaseVectorStoreDriver

@define
class MongoDbAtlasVectorStoreDriver(BaseVectorStoreDriver):
    connection_string: str = field(kw_only=True)
    database_name: str = field(kw_only=True)
    collection_name: str = field(kw_only=True)

    mongo_client: MongoClient = field(
        default=Factory(
            lambda self: MongoClient(self.connection_string), takes_self=True
        ),
        init=False,
    )
    collection: any = field(
        default=Factory(
            lambda self: self.mongo_client[self.database_name][self.collection_name],
            takes_self=True,
        ),
        init=False,
    )

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs
    ) -> str:
        if vector_id is None:
            result = self.collection.insert_one(
                {
                    "vector": vector,
                    "namespace": namespace,
                    "meta": meta,
                }
            )
            vector_id = str(result.inserted_id)  # convert ObjectId to str
        else:
            self.collection.replace_one(
                {"_id": ObjectId(vector_id)},  # convert str to ObjectId
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
        doc = self.collection.find_one({"_id": ObjectId(vector_id)})
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
        if namespace is None:
            cursor = self.collection.find()
        else:
            cursor = self.collection.find({"namespace": namespace})

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
