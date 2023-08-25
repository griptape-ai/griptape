from typing import Optional, Union, Tuple
from opensearchpy import OpenSearch, RequestsHttpConnection
from griptape import utils
from griptape.drivers import BaseVectorStoreDriver
from attr import define, field, Factory


@define
class OpenSearchVectorStoreDriver(BaseVectorStoreDriver):
    host: str = field(kw_only=True)
    port: int = field(default=443, kw_only=True)
    http_auth: Optional[Union[str, Tuple[str, str]]] = field(default=None, kw_only=True)
    use_ssl: bool = field(default=True, kw_only=True)
    verify_certs: bool = field(default=True, kw_only=True)
    index_name: str = field(kw_only=True)
    dimension: int = field(default=3, kw_only=True)

    client: OpenSearch = field(default=Factory(
        lambda self: OpenSearch(
            hosts=[{'host': self.host, 'port': self.port}],
            http_auth=self.http_auth,
            use_ssl=self.use_ssl,
            verify_certs=self.verify_certs,
            connection_class=RequestsHttpConnection
        ),
        takes_self=True
    ))

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:

        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))
        doc = {
            "vector": vector,
            "namespace": namespace,
            "metadata": meta
        }
        doc.update(kwargs)
        response = self.client.index(index=self.index_name, id=vector_id, body=doc)

        return response["_id"]

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        try:
            response = self.client.get(index=self.index_name, id=vector_id)
            if response["found"]:
                # Extracting the vector details
                vector_data = response["_source"]

                # Constructing the Entry object
                entry = BaseVectorStoreDriver.Entry(
                    id=vector_id,
                    meta=vector_data.get("metadata"),  # Assumes you have a metadata key in your vector data
                    vector=vector_data.get("vector"),  # Assumes you have a vector key in your vector data
                    namespace=vector_data.get("namespace")  # Assumes you have a namespace key in your vector data
                )
                return entry
            return None
        except Exception as e:
            print(f"Error while loading entry: {e}")
            return None

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:

        query_body = {
            "size": 10000,  # Retrieve up to 10,000 documents
            "query": {
                "match_all": {}  # Match all documents
            }
        }

        # If a namespace is provided, adjust the query to match vectors in that namespace
        if namespace:
            query_body["query"] = {
                "match": {
                    "namespace": namespace
                }
            }

        response = self.client.search(index=self.index_name, body=query_body)

        entries = []
        for hit in response["hits"]["hits"]:
            vector_data = hit["_source"]
            entry = BaseVectorStoreDriver.Entry(
                id=hit["_id"],
                vector=vector_data.get("vector"),
                meta=vector_data.get("metadata"),
                namespace=vector_data.get("namespace")
            )
            entries.append(entry)

        return entries

    def query(
            self,
            query_vector: list[float],
            count: Optional[int] = None,
            field_name: str = "vector",
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            include_metadata=True,
            **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        count = count if count else BaseVectorStoreDriver.DEFAULT_QUERY_COUNT

        # Base k-NN query
        query_body = {
            "size": count,
            "query": {
                "knn": {
                    field_name: {
                        "vector": query_vector,
                        "k": count
                    }
                }
            }
        }

        # If a namespace is provided, adjust the query to match vectors in that namespace
        if namespace:
            query_body["query"] = {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "namespace": namespace
                            }
                        },
                        {
                            "knn": {
                                field_name: {
                                    "vector": query_vector,
                                    "k": count
                                }
                            }
                        }
                    ]
                }
            }

        response = self.client.search(index=self.index_name, body=query_body)
        # After receiving the response

        return [
            BaseVectorStoreDriver.QueryResult(
                namespace=hit["_source"].get("namespace") if namespace else None,
                score=hit["_score"],
                vector=hit["_source"].get("vector") if include_vectors else None,
                meta=hit["_source"].get("metadata") if include_metadata else None
            )
            for hit in response["hits"]["hits"]
        ]

    def simple_query(self):
        query_body = {
            "size": 5,
            "query": {
                "match_all": {}
            }
        }
        print("Simple Query Body:", query_body)
        response = self.client.search(index=self.index_name, body=query_body)
        print("Response:", response)

        results = []
        if response and "hits" in response and "hits" in response["hits"]:
            for hit in response["hits"]["hits"]:
                results.append(BaseVectorStoreDriver.QueryResult(
                    namespace=hit["_source"].get("namespace"),
                    score=hit["_score"],
                    vector=hit["_source"].get("vector"),
                    meta=hit["_source"].get("metadata")
                ))
        return results

    def initialize_index(self):
        if not self.client.indices.exists(index=self.index_name):
            mapping = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "index.knn": True
                },
                "mappings": {
                    "properties": {
                        "vector": {
                            "type": "knn_vector",
                            "dimension": self.dimension
                        },
                        "namespace": {
                            "type": "keyword"
                        },
                        "metadata": {
                            "type": "object",
                            "enabled": True
                        }
                    }
                }
            }
            try:
                self.client.indices.create(index=self.index_name, body=mapping)
            except Exception as e:
                print(f"Error initializing the index: {e}")
