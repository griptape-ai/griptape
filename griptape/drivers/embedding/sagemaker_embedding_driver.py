import json
import boto3
from typing import Any
from attr import define, field, Factory
from griptape.drivers import BaseEmbeddingDriver


@define
class AmazonSagemakerEmbeddingDriver(BaseEmbeddingDriver):
    endpoint: str = field(kw_only=True)
    session: boto3.Session = field(
        default=Factory(lambda: boto3.Session()), kw_only=True
    )
    sagemaker_client: Any = field(
        default=Factory(
            lambda self: self.session.client("runtime.sagemaker"),
            takes_self=True,
        ),
        kw_only=True,
    )

    def try_embed_string(self, string: str) -> list[float]:
        # text_inputs can take a list of string and generate a list of embeddings
        # the length of the embedding key in the response will be the same as the text_inputs array
        payload = {"text_inputs": string}
        endpoint_response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint,
            ContentType="application/json",
            Body=json.dumps(payload).encode("utf-8"),
        )

        response = json.loads(
            endpoint_response.get("Body").read().decode("utf-8")
        )
        return response.get("embedding")[0]
