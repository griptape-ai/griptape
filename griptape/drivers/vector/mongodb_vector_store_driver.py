from typing import Optional
from pymongo import MongoClient
from griptape.drivers import BaseVectorStoreDriver
from attr import define, field, Factory

@define
class MongoDbAtlasVectorStoreDriver(BaseVectorStoreDriver):
    connection_string: str = field(kw_only=True)
    database_name: str = field(kw_only=True)
    collection_name: str = field(kw_only=True)

    mg: MongoClient = field(default=Factory(lambda self: MongoClient(self.connection_string), takes_self=True), kw_only=True)
    collection: any = field(default=Factory(lambda self: self.client[self.database_name][self.collection_name], takes_self=True), kw_only=True)

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        if vector_id is None:
            result = self.collection.insert_one({
                'vector': vector,
                'namespace': namespace,
                'meta': meta,
            })
            vector_id = result.inserted_id
        else:
            self.collection.replace_one(
                {'_id': vector_id},
                {
                    'vector': vector,
                    'namespace': namespace,
                    'meta': meta,
                },
                upsert=True
            )
        return vector_id

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        doc = self.collection.find_one({'_id': vector_id})
        if doc is None:
            return None
        else:
            return BaseVectorStoreDriver.Entry(
                id=doc['_id'],
                vector=doc['vector'],
                namespace=doc['namespace'],
                meta=doc['meta'],
            )

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        if namespace is None:
            cursor = self.collection.find()
        else:
            cursor = self.collection.find({'namespace': namespace})
        return [
            BaseVectorStoreDriver.Entry(
                id=doc['_id'],
                vector=doc['vector'],
                namespace=doc['namespace'],
                meta=doc['meta'],
            )
            for doc in cursor
        ]

    def query(
            self,
            query: str,
            count: Optional[int] = None,
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        raise NotImplementedError('Vector search not supported in MongoDB')

