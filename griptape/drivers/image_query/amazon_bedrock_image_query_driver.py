from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from attr import define, field, Factory
from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseMultiModelImageQueryDriver
from griptape.utils import import_optional_dependency
import json

if TYPE_CHECKING:
    import boto3


@define
class AmazonBedrockImageQueryDriver(BaseMultiModelImageQueryDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True), kw_only=True
    )
    max_output_tokens: Optional[int] = field(default=4096, kw_only=True, metadata={"serializable": True})

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        payload = self.image_query_model_driver.construct_image_query_request_parameters(query, images)

        response = self.bedrock_client.invoke_model(
            modelId=self.model, contentType="application/json", accept="application/json", body=json.dumps(payload)
        )

        response_body = json.loads(response.get("body").read())

        if response_body:
            return self.image_query_model_driver.process_output(response_body)
        else:
            raise Exception("Model response is empty")
