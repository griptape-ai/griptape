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
        service: Service name for AWS Signature v4. Values can be 'es' or 'aoss' for for OpenSearch Serverless. Defaults to 'es'.
        http_auth: The HTTP authentication credentials to use. Defaults to using credentials in the boto3 session.
        client: An optional OpenSearch client to use. Defaults to a new client using the host, port, http_auth, use_ssl, and verify_certs attributes.
    """

    session: Optional[Session] = field(default=None, kw_only=True)

    service: Optional[str] = field(default="es", kw_only=True)

    http_auth: Optional[str | Tuple[str, str]] = field(
        default=Factory(
            lambda self: import_optional_dependency("opensearchpy").AWSV4SignerAuth(
                self.session.get_credentials(), self.session.region_name, self.service
            ),
            takes_self=True,
        )
    )

    client: Optional[OpenSearch] = field(
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
