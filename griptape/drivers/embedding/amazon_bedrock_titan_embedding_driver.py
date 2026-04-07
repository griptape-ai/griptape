from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding import BaseEmbeddingDriver
from griptape.tokenizers.amazon_bedrock_tokenizer import AmazonBedrockTokenizer
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    import boto3
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

    from griptape.tokenizers.base_tokenizer import BaseTokenizer


@define
class AmazonBedrockTitanEmbeddingDriver(BaseEmbeddingDriver):
    """Amazon Bedrock Titan Embedding Driver.

    Attributes:
        model: Embedding model name. Defaults to DEFAULT_MODEL.
        tokenizer: Optionally provide custom `BedrockTitanTokenizer`.
        session: Optionally provide custom `boto3.Session`.
        client: Optionally provide custom `bedrock-runtime` client.
    """

    DEFAULT_MODEL = "amazon.titan-embed-text-v1"

    model: str = field(default=DEFAULT_MODEL, kw_only=True, metadata={"serializable": True})
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: AmazonBedrockTokenizer(model=self.model), takes_self=True),
        kw_only=True,
    )
    _client: Optional[BedrockRuntimeClient] = field(
        default=None, kw_only=True, alias="client", metadata={"serializable": False}
    )

    @lazy_property()
    def client(self) -> BedrockRuntimeClient:
        return self.session.client("bedrock-runtime")

    def try_embed_artifact(self, artifact: TextArtifact | ImageArtifact, **kwargs) -> list[float]:
        if isinstance(artifact, TextArtifact):
            return self.try_embed_chunk(artifact.value)
        return self._invoke_model({"inputImage": base64.b64encode(artifact.value).decode()})["embedding"]

    def try_embed_chunk(self, chunk: str, **kwargs) -> list[float]:
        return self._invoke_model(
            {
                "inputText": chunk,
            }
        )["embedding"]

    def _invoke_model(self, payload: dict) -> dict[str, Any]:
        response = self.client.invoke_model(
            body=json.dumps(payload),
            modelId=self.model,
            accept="application/json",
            contentType="application/json",
        )
        return json.loads(response.get("body").read())
