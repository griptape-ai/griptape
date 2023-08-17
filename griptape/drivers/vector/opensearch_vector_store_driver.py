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

    def upsert_vector(self, vector, vector_id: Optional[str] = None, **kwargs) -> str:
        # Your logic to upsert a vector into OpenSearch goes here
        pass

    def load_entry(self, vector_id: str) -> Optional[BaseVectorStoreDriver.Entry]:
        # Your logic to fetch a single entry based on vector ID goes here
        pass

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        """Load all document entries from the OpenSearch index."""
        raise NotImplementedError("Method needs to be adapted for OpenSearch.")

    def query(self, query: str, count: Optional[int] = None, namespace: Optional[str] = None, include_vectors: bool = False, include_metadata=True, **kwargs) -> list[BaseVectorStoreDriver.QueryResult]:
        """Query the OpenSearch index for documents."""
        raise NotImplementedError("Method needs to be adapted for OpenSearch.")

