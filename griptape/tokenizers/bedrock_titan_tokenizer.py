import json
import boto3
from attr import define, field, Factory
from typing import Any
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class BedrockTitanTokenizer(BaseTokenizer):
    DEFAULT_MODEL = 'amazon.titan-text-express-v1'
    DEFAULT_MAX_TOKENS = 4096

    session: boto3.Session = field(
        default=Factory(lambda: boto3.Session()), kw_only=True
    )
    stop_sequences: list[str] = field(factory=list, kw_only=True)
    model: str = field(kw_only=True)
    bedrock_client: Any = field(
        default=Factory(
            lambda self: self.session.client("bedrock-runtime"),
            takes_self=True,
        ),
        kw_only=True,
    )

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def token_count(self, text: str) -> int:
        payload = { "inputText": text }

        response = self.bedrock_client.invoke_model(
            body=json.dumps(payload),
            modelId=self.model,
            accept="application/json",
            contentType="application/json",
        )
        response_body = json.loads(response.get("body").read())

        return response_body['inputTextTokenCount']

    def encode(self, _: str) -> str:
        raise NotImplementedError("Method is not implemented: Amazon Bedrock does not provide a compatible tokenization API.")

    def decode(self, _: list[int]) -> str:
        raise NotImplementedError("Method is not implemented: Amazon Bedrock does not provide a compatible de-tokenization API.")

