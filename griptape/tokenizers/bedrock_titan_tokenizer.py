from __future__ import annotations
import json
from attr import define, field, Factory
from typing import Any, TYPE_CHECKING
from griptape.tokenizers import BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3


@define(frozen=True)
class BedrockTitanTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "amazon.titan-text-express-v1"
    DEFAULT_MAX_TOKENS = 4096

    DEFAULT_EMBEDDING_MODELS = "amazon.titan-embed-text-v1"

    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    stop_sequences: list[str] = field(factory=list, kw_only=True)
    model: str = field(kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True), kw_only=True
    )

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def count_tokens(self, text: str) -> int:
        payload = {"inputText": text}

        response = self.bedrock_client.invoke_model(
            body=json.dumps(payload), modelId=self.model, accept="application/json", contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())

        return response_body["inputTextTokenCount"]
