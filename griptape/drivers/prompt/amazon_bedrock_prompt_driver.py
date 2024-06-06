from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.drivers import BasePromptDriver
from griptape.artifacts import TextArtifact
from griptape.utils import import_optional_dependency
from griptape.tokenizers import SimpleTokenizer, BaseTokenizer

if TYPE_CHECKING:
    from griptape.utils import PromptStack
    import boto3


@define
class AmazonBedrockPromptDriver(BasePromptDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True), kw_only=True
    )
    additional_model_request_fields: dict = field(default=Factory(dict), kw_only=True)
    tokenizer: BaseTokenizer = field(default=Factory(lambda: SimpleTokenizer(characters_per_token=4)), kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        response = self.bedrock_client.converse(**self._base_params(prompt_stack))

        output_message = response["output"]["message"]
        output_content = output_message["content"][0]["text"]

        return TextArtifact(output_content)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        response = self.bedrock_client.converse_stream(**self._base_params(prompt_stack))

        stream = response.get("stream")
        if stream is not None:
            for event in stream:
                if "contentBlockDelta" in event:
                    yield TextArtifact(event["contentBlockDelta"]["delta"]["text"])
        else:
            raise Exception("model response is empty")

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        system_messages = [
            {"text": input.content} for input in prompt_stack.inputs if input.is_system() and input.content
        ]
        messages = [
            {"role": self.__to_amazon_bedrock_role(input), "content": [{"text": input.content}]}
            for input in prompt_stack.inputs
            if not input.is_system()
        ]

        return {
            "modelId": self.model,
            "messages": messages,
            "system": system_messages,
            "inferenceConfig": {"temperature": self.temperature},
            "additionalModelRequestFields": self.additional_model_request_fields,
        }

    def __to_amazon_bedrock_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"
