from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.drivers import BaseEmbeddingDriver
from griptape.tokenizers.amazon_bedrock_tokenizer import AmazonBedrockTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3

    from griptape.tokenizers.base_tokenizer import BaseTokenizer


@define
class AmazonBedrockCohereEmbeddingDriver(BaseEmbeddingDriver):
    """Amazon Bedrock Cohere Embedding Driver.

    Attributes:
        model: Embedding model name. Defaults to DEFAULT_MODEL.
        input_type: Defaults to `search_query`. Prepends special tokens to differentiate each type from one another:
            `search_document` when you encode documents for embeddings that you store in a vector database.
            `search_query` when querying your vector DB to find relevant documents.
        session: Optionally provide custom `boto3.Session`.
        tokenizer: Optionally provide custom `BedrockCohereTokenizer`.
        bedrock_client: Optionally provide custom `bedrock-runtime` client.
    """

    DEFAULT_MODEL = "cohere.embed-english-v3"

    model: str = field(default=DEFAULT_MODEL, kw_only=True)
    input_type: str = field(default="search_query", kw_only=True)
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: AmazonBedrockTokenizer(model=self.model), takes_self=True),
        kw_only=True,
    )
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True),
        kw_only=True,
    )

    def try_embed_chunk(self, chunk: str) -> list[float]:
        payload = {"input_type": self.input_type, "texts": [chunk]}

        response = self.bedrock_client.invoke_model(
            body=json.dumps(payload),
            modelId=self.model,
            accept="*/*",
            contentType="application/json",
        )
        response_body = json.loads(response.get("body").read())

        return response_body.get("embeddings")[0]
