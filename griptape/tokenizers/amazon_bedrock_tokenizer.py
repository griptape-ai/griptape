import os
import json
import boto3
from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AmazonBedrockTokenizer(BaseTokenizer):
    DEFAULT_MODEL = 'amazon.titan-e1t-medium'
    DEFAULT_MAX_TOKENS = 4096
    
    stop_sequences: list[str] = field(
        default=Factory(lambda: []),
        kw_only=True
    )

    session: boto3.Session = field(
        default=Factory(lambda: boto3.Session()), kw_only=True
    )
    model: str = field(default=DEFAULT_MODEL, kw_only=True)
    bedrock_client: boto3.client = field(
        default=Factory(
            lambda self: self.session.client("bedrock"),
            takes_self=True,
        ),
        kw_only=True,
    )

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def token_count(self, text: str) -> int:
        text = text.replace(os.linesep, " ")

        payload = {"inputText": text}

        response = self.bedrock_client.invoke_model(
            body=json.dumps(payload),
            modelId=self.model,
            accept="application/json",
            contentType="application/json",
        )
        response_body = json.loads(response.get("body").read())

        return response_body.get("inputTextTokenCount")

    def encode(self, _: list[int]) -> str:
        raise NotImplementedError("Method is not implemented: Amazon Bedrock does not provide a compatible tokenization API.")

    def decode(self, _: list[int]) -> str:
        raise NotImplementedError("Method is not implemented: Amazon Bedrock does not provide a compatible de-tokenization API.")
