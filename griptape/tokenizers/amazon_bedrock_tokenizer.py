import json
import boto3
from attr import define, field, Factory
from typing import Any
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class AmazonBedrockTokenizer(BaseTokenizer):
    MODEL_TO_MAX_TOKENS = {
        "anthropic.claude-v1": 8192,
        "anthropic.claude-v2": 8192,
        "anthropic.claude-instant-v1": 8192,
        "amazon.titan-tg1-large": 4096,
        "ai21.j2-ultra": 8192,
        "ai21.j2-mid": 8192,
    }

    session: boto3.Session = field(
        default=Factory(lambda: boto3.Session()), kw_only=True
    )
    stop_sequences: list[str] = field(factory=list, kw_only=True)

    model: str = field(kw_only=True)
    bedrock_client: Any = field(
        default=Factory(
            lambda self: self.session.client("bedrock"),
            takes_self=True,
        ),
        kw_only=True,
    )

    @property
    def max_tokens(self) -> int:
        return self.MODEL_TO_MAX_TOKENS[self.model]

    def token_count(self, text: str) -> int:
        payload = self.__model_to_input_params(text)

        response = self.bedrock_client.invoke_model(
            body=json.dumps(payload),
            modelId=self.model,
            accept="application/json",
            contentType="application/json",
        )
        response_body = json.loads(response.get("body").read())

        return self.__process_output(response_body)

    def encode(self, _: list[int]) -> str:
        raise NotImplementedError("Method is not implemented: Amazon Bedrock does not provide a compatible tokenization API.")

    def decode(self, _: list[int]) -> str:
        raise NotImplementedError("Method is not implemented: Amazon Bedrock does not provide a compatible de-tokenization API.")

    def __model_to_input_params(self, text: str) -> dict:
        if self.model.startswith("ai21"):
            return {"prompt": text}
        elif self.model.startswith("amazon"):
            return {"inputText": text}
        else:
            raise ValueError(f"{self.model} is not a valid Amazon Bedrock model for tokenization.")

    def __process_output(self, output: dict) -> int:
        if self.model.startswith("ai21"):
            return len(output["prompt"]["tokens"])
        elif self.model.startswith("amazon"):
            return output["inputTextTokenCount"]
        else:
            raise ValueError(f"{self.model} is not a valid Amazon Bedrock model for tokenization.")
