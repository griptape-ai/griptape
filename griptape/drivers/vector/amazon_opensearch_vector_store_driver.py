import boto3
from requests_aws4auth import AWS4Auth
from attr import define, field, Factory
from typing import Optional, Union, Tuple
from griptape.drivers import OpenSearchVectorStoreDriver
from opensearchpy import OpenSearch, RequestsHttpConnection


@define
class AmazonOpenSearchVectorStoreDriver(OpenSearchVectorStoreDriver):
    """A Vector Store Driver for Amazon OpenSearch.

    Attributes:
        session: The boto3 session to use.
        http_auth: The HTTP authentication credentials to use. Defaults to using credentials in the boto3 session.
        client: An optional OpenSearch client to use. Defaults to a new client using the host, port, http_auth, use_ssl, and verify_certs attributes.
    """
    session: boto3.session.Session = field(kw_only=True)

    http_auth: Optional[Union[str, Tuple[str, str]]] = field(
        default=Factory(
            lambda self: AWS4Auth(
                self.session.get_credentials().access_key,
                self.session.get_credentials().secret_key,
                self.session.region_name,
                'es'
            ),
            takes_self=True)
    )

    client: Optional[OpenSearch] = field(
        default=Factory(
            lambda self: OpenSearch(
                hosts=[{'host': self.host, 'port': self.port}],
                http_auth=self.http_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                connection_class=RequestsHttpConnection
            ),
            takes_self=True
        )
    )
