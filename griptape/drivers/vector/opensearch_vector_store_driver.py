from typing import Optional
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from griptape import utils
from griptape.drivers import BaseVectorStoreDriver
from attr import define, field


@define
class OpenSearchVectorStoreDriver(BaseVectorStoreDriver):
    host: str = field(kw_only=True)
    aws_access_key: str = field(kw_only=True)
    aws_secret_key: str = field(kw_only=True)
    region: str = field(kw_only=True)
    index_name: str = field(kw_only=True)

    client: Elasticsearch = field(init=False)

    def __attrs_post_init__(self) -> None:
        aws_auth = AWS4Auth(self.aws_access_key, self.aws_secret_key, self.region, 'es')
        self.client = Elasticsearch(
            hosts=[{'host': self.host, 'port': 443}],
            http_auth=aws_auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

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
            # Handle exceptions like "document not found" or any other issues
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
            count: Optional[int] = 10,
            field_name: str = "vector",
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            include_metadata=True,
            **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """
        Query the OpenSearch index for k nearest neighbors to the given vector.

        Args:
            - query_vector: The vector used for the k-NN search.
            - count: The number of neighbors you want the query to return.
            - field_name: The field containing the vectors in the OpenSearch index.
            - namespace: An optional namespace filter.
            - include_vectors: Whether to include vectors in the results.
            - include_metadata: Whether to include metadata in the results.
            - **kwargs: Additional arguments.

        Returns:
            A list of QueryResult objects.
        """

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

        results = []
        for hit in response["hits"]["hits"]:
            vector_data = hit["_source"]

            # Create the QueryResult object.
            # This is an approximation since the exact structure of QueryResult is not provided
            result = BaseVectorStoreDriver.QueryResult(
                id=hit["_id"],
                score=hit["_score"],
                vector=vector_data.get("vector") if include_vectors else None,
                meta=vector_data.get("metadata") if include_metadata else None
            )
            results.append(result)

        return results


