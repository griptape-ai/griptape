from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import Attribute, Factory, define, field

from griptape.artifacts import ImageArtifact, ImageUrlArtifact
from griptape.common import (
    BaseMessageContent,
    DeltaMessage,
    ImageMessageContent,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
    observable,
)
from griptape.configs import Defaults
from griptape.drivers.prompt import BasePromptDriver
from griptape.tokenizers import HuggingFaceTokenizer
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from collections.abc import Iterator

    from huggingface_hub import ChatCompletionOutput, InferenceClient

    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class HuggingFaceHubPromptDriver(BasePromptDriver):
    """Hugging Face Hub Prompt Driver.

    Attributes:
        api_token: Hugging Face Hub API token.
        use_gpu: Use GPU during model run.
        model: Hugging Face Hub model name.
        client: Custom `InferenceApi`.
        tokenizer: Custom `HuggingFaceTokenizer`.
    """

    api_token: str = field(kw_only=True, metadata={"serializable": True})
    max_tokens: int = field(default=250, kw_only=True, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    structured_output_strategy: StructuredOutputStrategy = field(
        default="native", kw_only=True, metadata={"serializable": True}
    )
    tokenizer: HuggingFaceTokenizer = field(
        default=Factory(
            lambda self: HuggingFaceTokenizer(model=self.model, max_output_tokens=self.max_tokens),
            takes_self=True,
        ),
        kw_only=True,
    )
    _client: InferenceClient | None = field(
        default=None, kw_only=True, alias="client", metadata={"serializable": False}
    )

    @lazy_property()
    def client(self) -> InferenceClient:
        return import_optional_dependency("huggingface_hub").InferenceClient(
            model=self.model,
            token=self.api_token,
        )

    @structured_output_strategy.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_structured_output_strategy(self, _: Attribute, value: str) -> str:
        if value == "tool":
            raise ValueError(f"{__class__.__name__} does not support `{value}` structured output strategy.")

        return value

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        params = self._base_params(prompt_stack)
        logger.debug(params)

        response = self.client.chat_completion(**params)
        logger.debug(response)

        return self._to_message(response)

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        params = self._base_params(prompt_stack)
        logger.debug({"stream": True, **params})

        for chunk in self.client.chat_completion(**params, stream=True):
            logger.debug(chunk)

            if chunk.usage is not None:
                yield DeltaMessage(
                    usage=DeltaMessage.Usage(
                        input_tokens=chunk.usage.prompt_tokens,
                        output_tokens=chunk.usage.completion_tokens,
                    )
                )

            if chunk.choices:
                delta = chunk.choices[0].delta

                if delta.content is not None:
                    yield DeltaMessage(content=TextDeltaMessageContent(delta.content, index=0))

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = {
            "messages": self._prompt_stack_to_messages(prompt_stack),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            **({"stream_options": {"include_usage": True}} if self.stream else {}),
            **self.extra_params,
        }

        if prompt_stack.output_schema is not None and self.structured_output_strategy == "native":
            output_schema = prompt_stack.to_output_json_schema()
            # Text Generation Inference compiles this schema into a grammar and rejects the
            # `$schema` and `$id` metadata keys.
            del output_schema["$schema"]
            del output_schema["$id"]
            params["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "Output", "schema": output_schema, "strict": True},
            }

        return params

    def _to_message(self, response: ChatCompletionOutput) -> Message:
        if len(response.choices) != 1:
            raise Exception("Completion with more than one choice is not supported yet.")

        message = Message(
            content=response.choices[0].message.content or "",
            role=Message.ASSISTANT_ROLE,
        )

        if response.usage is not None:
            message.usage = Message.Usage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
            )

        return message

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        messages = []

        for message in prompt_stack.messages:
            # Text-only messages can be sent as a plain string, which every model accepts.
            if message.has_all_content_type(TextMessageContent):
                messages.append({"role": message.role, "content": message.to_text()})
            else:
                messages.append(
                    {
                        "role": message.role,
                        "content": [self.__to_message_content(content) for content in message.content],
                    }
                )

        return messages

    def __to_message_content(self, content: BaseMessageContent) -> dict:
        if isinstance(content, TextMessageContent):
            return {"type": "text", "text": content.artifact.to_text()}
        if isinstance(content, ImageMessageContent):
            if isinstance(content.artifact, ImageArtifact):
                return {
                    "type": "image_url",
                    "image_url": {"url": f"data:{content.artifact.mime_type};base64,{content.artifact.base64}"},
                }
            if isinstance(content.artifact, ImageUrlArtifact):
                return {"type": "image_url", "image_url": {"url": content.artifact.value}}
            raise ValueError(f"Unsupported image artifact type: {type(content.artifact)}")
        raise ValueError(f"Unsupported content type: {type(content)}")
