from typing import Optional, Dict, Any, List
from griptape.drivers import BaseVectorStoreDriver
from pymongo import MongoClient
from attr import define, field, Factory
import logging


@define
class MongoDbAtlasVectorStoreDriver(BaseVectorStoreDriver):
    connection_string: str = field(kw_only=True)
    database_name: str = field(kw_only=True)
    collection_name: str = field(kw_only=True)
    client: MongoClient = field(init=False)
    collection = field(init=False)

    def __attrs_post_init__(self) -> None:
        try:
            self.client = MongoClient(self.connection_string)
            self.collection = self.client[self.database_name][self.collection_name]
            logging.info("Connected to MongoDB Atlas successfully!")
        except Exception as e:
            logging.error("Could not connect to MongoDB Atlas!")
            logging.error(str(e))

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        try:
            document = {"vector": vector, "meta": meta, "namespace": namespace}
            if vector_id:
                document["_id"] = vector_id
            result = self.collection.replace_one({"_id": vector_id}, document, upsert=True)
            return result.upserted_id or vector_id
        except Exception as e:
            logging.error("Error during vector upsert!")
            logging.error(str(e))

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        try:
            document = self.collection.find_one({"_id": vector_id})
            if document:
                return BaseVectorStoreDriver.Entry(
                    id=document["_id"],
                    vector=document["vector"],
                    meta=document["meta"],
                    namespace=document["namespace"]
                )
            else:
                return None
        except Exception as e:
            logging.error(f"Error loading vector {vector_id}!")
            logging.error(str(e))

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        try:
            query = {"namespace": namespace} if namespace else {}
            documents = self.collection.find(query)
            return [
                BaseVectorStoreDriver.Entry(
                    id=doc["_id"],
                    vector=doc["vector"],
                    meta=doc["meta"],
                    namespace=doc["namespace"]
                )
                for doc in documents
            ]
        except Exception as e:
            logging.error(f"Error loading entries!")
            logging.error(str(e))

    def query(
            self,
            query: str,
            count: Optional[int] = None,
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        logging.error("Vector similarity search is not supported by MongoDB.")
        return []
