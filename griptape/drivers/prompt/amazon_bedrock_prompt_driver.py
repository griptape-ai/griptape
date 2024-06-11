from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    BaseDeltaPromptStackContent,
    DeltaPromptStackElement,
    PromptStackElement,
    DeltaTextPromptStackContent,
    BasePromptStackContent,
    TextPromptStackContent,
    ImagePromptStackContent,
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

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        response = self.bedrock_client.converse(**self._base_params(prompt_stack))

        usage = response["usage"]
        output_message = response["output"]["message"]

        return PromptStackElement(
            content=[self._message_content_to_prompt_stack_content(content) for content in output_message["content"]],
            role=output_message["role"],
            usage=PromptStackElement.Usage(input_tokens=usage["inputTokens"], output_tokens=usage["outputTokens"]),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        response = self.bedrock_client.converse_stream(**self._base_params(prompt_stack))

        stream = response.get("stream")
        if stream is not None:
            for event in stream:
                if "messageStart" in event:
                    yield DeltaPromptStackElement(role=event["messageStart"]["role"])
                elif "contentBlockDelta" in event:
                    content_block_delta = event["contentBlockDelta"]
                    yield DeltaTextPromptStackContent(
                        TextArtifact(value=content_block_delta["delta"]["text"]),
                        index=content_block_delta["contentBlockIndex"],
                    )
                elif "metadata" in event:
                    usage = event["metadata"]["usage"]
                    yield DeltaPromptStackElement(
                        delta_usage=DeltaPromptStackElement.DeltaUsage(
                            input_tokens=usage["inputTokens"], output_tokens=usage["outputTokens"]
                        )
                    )
        else:
            raise Exception("model response is empty")

    def _prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        content = [self._prompt_stack_content_to_message_content(content) for content in prompt_input.content]

        if prompt_input.is_assistant():
            return {"role": "assistant", "content": content}
        else:
            return {"role": "user", "content": content}

    def _prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return {"text": content.artifact.to_text()}
        elif isinstance(content, ImagePromptStackContent):
            return {
                "source": {"type": "base64", "format": content.artifact.media_type, "bytes": content.artifact.value}
            }
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def _message_content_to_prompt_stack_content(self, message_content: dict) -> BasePromptStackContent:
        if "text " in message_content:
            return TextPromptStackContent(TextArtifact(message_content["text"]))
        else:
            raise ValueError(f"Unsupported message content type: {message_content['text']}")

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        system_messages = [
            self._prompt_stack_input_to_message(input)
            for input in prompt_stack.inputs
            if input.is_system() and input.content
        ]
        messages = [
            self._prompt_stack_input_to_message(input) for input in prompt_stack.inputs if not input.is_system()
        ]

        return {
            "modelId": self.model,
            "messages": messages,
            "system": system_messages,
            "inferenceConfig": {"temperature": self.temperature},
            "additionalModelRequestFields": self.additional_model_request_fields,
        }
