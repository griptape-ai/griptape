from __future__ import annotations
from typing import TYPE_CHECKING
import json
from typing import Any

from attr import Factory, define, field

from griptape.drivers import BaseMultiModelEmbeddingDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingModelDriver
    import boto3


@define
class AmazonSageMakerEmbeddingDriver(BaseMultiModelEmbeddingDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    sagemaker_client: Any = field(
        default=Factory(lambda self: self.session.client("sagemaker-runtime"), takes_self=True), kw_only=True
    )
    embedding_model_driver: BaseEmbeddingModelDriver = field(kw_only=True)

    def try_embed_chunk(self, chunk: str) -> list[float]:
        payload = self.embedding_model_driver.chunk_to_model_params(chunk)
        endpoint_response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.model, ContentType="application/x-text", Body=json.dumps(payload).encode("utf-8")
        )

        response = json.loads(endpoint_response.get("Body").read().decode("utf-8"))
        return self.embedding_model_driver.process_output(response)
