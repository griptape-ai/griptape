from __future__ import annotations
import json
from attr import define, field, Factory
from typing import TYPE_CHECKING, Any
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    import boto3


@define(frozen=True)
class BedrockJurassicTokenizer(BaseTokenizer):
    DEFAULT_MODEL = "ai21.j2-ultra-v1"
    DEFAULT_MAX_TOKENS = 8192

    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    model: str = field(kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True), kw_only=True
    )

    @property
    def max_tokens(self) -> int:
        return self.DEFAULT_MAX_TOKENS

    def count_tokens(self, text: str) -> int:
        payload = {"prompt": text}

        response = self.bedrock_client.invoke_model(
            body=json.dumps(payload), modelId=self.model, accept="application/json", contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())

        return len(response_body["prompt"]["tokens"])
