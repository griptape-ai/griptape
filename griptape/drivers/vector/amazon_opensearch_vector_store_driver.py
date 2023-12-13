from __future__ import annotations
from attr import define, field, Factory
from typing import Optional, Tuple, TYPE_CHECKING
from griptape.drivers import OpenSearchVectorStoreDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from boto3 import Session
    from opensearchpy import OpenSearch


@define
class AmazonOpenSearchVectorStoreDriver(OpenSearchVectorStoreDriver):
    """A Vector Store Driver for Amazon OpenSearch.

    Attributes:
        session: The boto3 session to use.
        http_auth: The HTTP authentication credentials to use. Defaults to using credentials in the boto3 session.
        client: An optional OpenSearch client to use. Defaults to a new client using the host, port, http_auth, use_ssl, and verify_certs attributes.
    """

    session: Session = field(kw_only=True)

    http_auth: str | tuple[str, str] | None = field(
        default=Factory(
            lambda self: import_optional_dependency("requests_aws4auth").AWS4Auth(
                self.session.get_credentials().access_key,
                self.session.get_credentials().secret_key,
                self.session.region_name,
                "es",
            ),
            takes_self=True,
        )
    )

    client: OpenSearch | None = field(
        default=Factory(
            lambda self: import_optional_dependency("opensearchpy").OpenSearch(
                hosts=[{"host": self.host, "port": self.port}],
                http_auth=self.http_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                connection_class=import_optional_dependency("opensearchpy").RequestsHttpConnection,
            ),
            takes_self=True,
        )
    )
