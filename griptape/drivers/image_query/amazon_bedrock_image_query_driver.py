from __future__ import annotations

import json
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.drivers import BaseMultiModelImageQueryDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    import boto3
    from mypy_boto3_bedrock import BedrockClient

    from griptape.artifacts import ImageArtifact, TextArtifact


@define
class AmazonBedrockImageQueryDriver(BaseMultiModelImageQueryDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    _client: BedrockClient = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> BedrockClient:
        return self.session.client("bedrock-runtime")

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        payload = self.image_query_model_driver.image_query_request_parameters(query, images, self.max_tokens)

        response = self.client.invoke_model(
            modelId=self.model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload),
        )

        response_body = json.loads(response.get("body").read())

        if response_body is None:
            raise ValueError("Model response is empty")

        try:
            return self.image_query_model_driver.process_output(response_body)
        except Exception as e:
            raise ValueError(f"Output is unable to be processed as returned {e}") from e
