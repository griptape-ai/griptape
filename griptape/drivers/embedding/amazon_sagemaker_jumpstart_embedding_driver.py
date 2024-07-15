from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.drivers import BaseEmbeddingDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3


@define
class AmazonSageMakerJumpstartEmbeddingDriver(BaseEmbeddingDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    sagemaker_client: Any = field(
        default=Factory(lambda self: self.session.client("sagemaker-runtime"), takes_self=True),
        kw_only=True,
    )
    endpoint: str = field(kw_only=True, metadata={"serializable": True})
    custom_attributes: str = field(default="accept_eula=true", kw_only=True, metadata={"serializable": True})
    inference_component_name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})

    def try_embed_chunk(self, chunk: str) -> list[float]:
        payload = {"text_inputs": chunk, "mode": "embedding"}

        endpoint_response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint,
            ContentType="application/json",
            Body=json.dumps(payload).encode("utf-8"),
            CustomAttributes=self.custom_attributes,
            **(
                {"InferenceComponentName": self.inference_component_name}
                if self.inference_component_name is not None
                else {}
            ),
        )

        response = json.loads(endpoint_response.get("Body").read().decode("utf-8"))

        if "embedding" in response:
            embedding = response["embedding"]

            if embedding:
                if isinstance(embedding[0], list):
                    return embedding[0]
                else:
                    return embedding
            else:
                raise ValueError("model response is empty")
        else:
            raise ValueError("invalid response from model")
