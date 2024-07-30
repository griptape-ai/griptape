from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.drivers import OpenSearchVectorStoreDriver
from griptape.utils import import_optional_dependency, str_to_hash

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

    session: Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    service: str = field(default="es", kw_only=True)
    http_auth: str | tuple[str, str] = field(
        default=Factory(
            lambda self: import_optional_dependency("opensearchpy").AWSV4SignerAuth(
                self.session.get_credentials(),
                self.session.region_name,
                self.service,
            ),
            takes_self=True,
        ),
    )

    client: OpenSearch = field(
        default=Factory(
            lambda self: import_optional_dependency("opensearchpy").OpenSearch(
                hosts=[{"host": self.host, "port": self.port}],
                http_auth=self.http_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                connection_class=import_optional_dependency("opensearchpy").RequestsHttpConnection,
            ),
            takes_self=True,
        ),
    )

    def upsert_vector(
        self,
        vector: list[float],
        *,
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str:
        """Inserts or updates a vector in OpenSearch.

        If a vector with the given vector ID already exists, it is updated; otherwise, a new vector is inserted.
        Metadata associated with the vector can also be provided.
        """
        vector_id = vector_id or str_to_hash(str(vector))
        doc = {"vector": vector, "namespace": namespace, "metadata": meta}
        doc.update(kwargs)
        if self.service == "aoss":
            response = self.client.index(index=self.index_name, body=doc)
        else:
            response = self.client.index(index=self.index_name, id=vector_id, body=doc)

        return response["_id"]
