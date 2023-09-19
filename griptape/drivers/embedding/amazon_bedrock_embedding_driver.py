import json
import os
import boto3
from typing import Any
from attr import define, field, Factory
from griptape.drivers import BaseEmbeddingDriver
from griptape.tokenizers import AmazonBedrockTokenizer


@define
class AmazonBedrockEmbeddingDriver(BaseEmbeddingDriver):
    DEFAULT_MODEL = "amazon.titan-e1t-medium"

    dimensions: int = field(default=1536, kw_only=True)
    model: str = field(default=DEFAULT_MODEL, kw_only=True)
    tokenizer: AmazonBedrockTokenizer = field(
        default=Factory(
            lambda self: AmazonBedrockTokenizer(model=self.model), takes_self=True
        ),
        kw_only=True,
    )
    session: boto3.Session = field(
        default=Factory(lambda: boto3.Session()), kw_only=True
    )
    bedrock_client: Any = field(
        default=Factory(
            lambda self: self.session.client("bedrock"),
            takes_self=True,
        ),
        kw_only=True,
    )

    def try_embed_string(self, string: str) -> list[float]:
        text = string.replace(os.linesep, " ")

        payload = { "inputText": text }

        response = self.bedrock_client.invoke_model(
            body=json.dumps(payload),
            modelId=self.model,
            accept='application/json',
            contentType='application/json'
        )
        response_body = json.loads(response.get("body").read())

        return response_body.get("embedding")
