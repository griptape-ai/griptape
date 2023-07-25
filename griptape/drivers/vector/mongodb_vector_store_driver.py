from typing import Optional
from pymongo import MongoClient, errors
from griptape import utils
from griptape.drivers import BaseVectorStoreDriver
from attr import define, field
import logging

@define
class MongoDbAtlasVectorStoreDriver(BaseVectorStoreDriver):
    client: MongoClient = field(init=False)
    db_name: str = field(kw_only=True)
    collection_name: str = field(kw_only=True)
    connection_string: str = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
        except errors.PyMongoError as e:
            logging.error(f"Error occurred while initializing MongoDB Atlas client: {str(e)}")
            raise

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs
    ) -> str:
        try:
            vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))
            doc = {'_id': vector_id, 'vector': vector, 'namespace': namespace, 'meta': meta}
            self.collection.replace_one({'_id': vector_id}, doc, upsert=True)
            return vector_id
        except errors.PyMongoError as e:
            logging.error(f"Error occurred while upserting vector: {str(e)}")
            raise

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        try:
            doc = self.collection.find_one({'_id': vector_id, 'namespace': namespace})
            if doc is not None:
                return BaseVectorStoreDriver.Entry(id=doc['_id'], vector=doc['vector'], meta=doc['meta'], namespace=doc['namespace'])
            else:
                return None
        except errors.PyMongoError as e:
            logging.error(f"Error occurred while loading entry: {str(e)}")
            raise

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        try:
            entries = []
            for doc in self.collection.find({'namespace': namespace}):
                entries.append(BaseVectorStoreDriver.Entry(id=doc['_id'], vector=doc['vector'], meta=doc['meta'], namespace=doc['namespace']))
            return entries
        except errors.PyMongoError as e:
            logging.error(f"Error occurred while loading entries: {str(e)}")
            raise

    def query(
        self,
        query: str,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        raise NotImplementedError("Vector similarity search not supported by MongoDB.")
