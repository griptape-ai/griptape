from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    BaseMessageContent,
    DeltaMessage,
    TextDeltaMessageContent,
    ImageMessageContent,
    PromptStack,
    Message,
    TextMessageContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, GoogleTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel
    from google.generativeai.types import ContentDict, GenerateContentResponse


@define
class GooglePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Google API key.
        model: Google model name.
        model_client: Custom `GenerativeModel` client.
        top_p: Optional value for top_p.
        top_k: Optional value for top_k.
    """

    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    model_client: Any = field(default=Factory(lambda self: self._default_model_client(), takes_self=True), kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> Message:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        messages = self._prompt_stack_to_messages(prompt_stack)
        response: GenerateContentResponse = self.model_client.generate_content(
            messages,
            generation_config=GenerationConfig(
                stop_sequences=self.tokenizer.stop_sequences,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            ),
        )

        usage_metadata = response.usage_metadata

        return Message(
            content=[TextMessageContent(TextArtifact(response.text))],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens=usage_metadata.prompt_token_count, output_tokens=usage_metadata.candidates_token_count
            ),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        messages = self._prompt_stack_to_messages(prompt_stack)
        response: Iterator[GenerateContentResponse] = self.model_client.generate_content(
            messages,
            stream=True,
            generation_config=GenerationConfig(
                stop_sequences=self.tokenizer.stop_sequences,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            ),
        )

        prompt_token_count = None
        for chunk in response:
            usage_metadata = chunk.usage_metadata

            # Only want to output the prompt token count once since it is static each chunk
            if prompt_token_count is None:
                prompt_token_count = usage_metadata.prompt_token_count
                yield DeltaMessage(
                    content=TextDeltaMessageContent(chunk.text),
                    role=Message.ASSISTANT_ROLE,
                    usage=DeltaMessage.Usage(
                        input_tokens=usage_metadata.prompt_token_count,
                        output_tokens=usage_metadata.candidates_token_count,
                    ),
                )
            else:
                yield DeltaMessage(
                    content=TextDeltaMessageContent(chunk.text),
                    role=Message.ASSISTANT_ROLE,
                    usage=DeltaMessage.Usage(output_tokens=usage_metadata.candidates_token_count),
                )

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        inputs = [
            {"role": self.__to_role(message), "parts": self.__to_content(message)}
            for message in prompt_stack.messages
            if not message.is_system()
        ]

        # Gemini does not have the notion of a system message, so we insert it as part of the first message in the history.
        system_messages = prompt_stack.system_messages
        if system_messages:
            inputs[0]["parts"].insert(0, system_messages[0].to_text())

        return inputs

    def __prompt_stack_content_message_content(self, content: BaseMessageContent) -> ContentDict | str:
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict

        if isinstance(content, TextMessageContent):
            return content.artifact.to_text()
        elif isinstance(content, ImageMessageContent):
            return ContentDict(mime_type=content.artifact.mime_type, data=content.artifact.value)
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __to_role(self, message: Message) -> str:
        if message.is_assistant():
            return "model"
        else:
            return "user"

    def __to_content(self, message: Message) -> list[ContentDict | str]:
        return [self.__prompt_stack_content_message_content(content) for content in message.content]
