from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    DeltaMessage,
    Message,
    TextDeltaMessageContent,
    BaseMessageContent,
    TextMessageContent,
    ImageMessageContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AmazonBedrockTokenizer, BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3

    from griptape.common import PromptStack


@define
class AmazonBedrockPromptDriver(BasePromptDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True), kw_only=True
    )
    additional_model_request_fields: dict = field(default=Factory(dict), kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: AmazonBedrockTokenizer(model=self.model), takes_self=True), kw_only=True
    )

    def try_run(self, prompt_stack: PromptStack) -> Message:
        response = self.bedrock_client.converse(**self._base_params(prompt_stack))

        usage = response["usage"]
        output_message = response["output"]["message"]

        return Message(
            content=[TextMessageContent(TextArtifact(content["text"])) for content in output_message["content"]],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=usage["inputTokens"], output_tokens=usage["outputTokens"]),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        response = self.bedrock_client.converse_stream(**self._base_params(prompt_stack))

        stream = response.get("stream")
        if stream is not None:
            for event in stream:
                if "contentBlockDelta" in event:
                    content_block_delta = event["contentBlockDelta"]
                    yield DeltaMessage(
                        content=TextDeltaMessageContent(
                            content_block_delta["delta"]["text"], index=content_block_delta["contentBlockIndex"]
                        )
                    )
                elif "metadata" in event:
                    usage = event["metadata"]["usage"]
                    yield DeltaMessage(
                        usage=DeltaMessage.Usage(input_tokens=usage["inputTokens"], output_tokens=usage["outputTokens"])
                    )
        else:
            raise Exception("model response is empty")

    def _prompt_stack_messages_to_messages(self, messages: list[Message]) -> list[dict]:
        return [
            {
                "role": self.__to_role(message),
                "content": [self.__prompt_stack_content_message_content(content) for content in message.content],
            }
            for message in messages
        ]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        system_messages = [{"text": message.to_text()} for message in prompt_stack.system_messages]

        messages = self._prompt_stack_messages_to_messages(
            [message for message in prompt_stack.messages if not message.is_system()]
        )

        return {
            "modelId": self.model,
            "messages": messages,
            "system": system_messages,
            "inferenceConfig": {"temperature": self.temperature},
            "additionalModelRequestFields": self.additional_model_request_fields,
        }

    def __prompt_stack_content_message_content(self, content: BaseMessageContent) -> dict:
        if isinstance(content, TextMessageContent):
            return {"text": content.artifact.to_text()}
        elif isinstance(content, ImageMessageContent):
            return {"image": {"format": content.artifact.format, "source": {"bytes": content.artifact.value}}}
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __to_role(self, message: Message) -> str:
        if message.is_assistant():
            return "assistant"
        else:
            return "user"
