from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import CohereTokenizer
from griptape.common import (
    PromptStack,
    Message,
    DeltaMessage,
    TextMessageContent,
    BaseMessageContent,
    TextDeltaMessageContent,
)
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from cohere import Client


@define(kw_only=True)
class CoherePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Cohere API key.
        model: 	Cohere model name.
        client: Custom `cohere.Client`.
    """

    api_key: str = field(metadata={"serializable": False})
    model: str = field(metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True)
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True)
    )

    def try_run(self, prompt_stack: PromptStack) -> Message:
        result = self.client.chat(**self._base_params(prompt_stack))
        usage = result.meta.tokens

        return Message(
            content=[TextMessageContent(TextArtifact(result.text))],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        result = self.client.chat_stream(**self._base_params(prompt_stack))

        for event in result:
            if event.event_type == "text-generation":
                yield DeltaMessage(content=TextDeltaMessageContent(event.text, index=0))
            elif event.event_type == "stream-end":
                usage = event.response.meta.tokens

                yield DeltaMessage(
                    usage=DeltaMessage.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens)
                )

    def _prompt_stack_messages_to_messages(self, messages: list[Message]) -> list[dict]:
        return [
            {
                "role": self.__to_role(message),
                "content": [self.__prompt_stack_content_message_content(content) for content in message.content],
            }
            for message in messages
        ]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        last_input = prompt_stack.messages[-1]
        user_message = last_input.to_text()

        history_messages = self._prompt_stack_messages_to_messages(
            [message for message in prompt_stack.messages[:-1] if not message.is_system()]
        )

        system_messages = prompt_stack.system_messages
        preamble = system_messages[0].to_text() if system_messages else None

        return {
            "message": user_message,
            "chat_history": history_messages,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "max_tokens": self.max_tokens,
            **({"preamble": preamble} if preamble else {}),
        }

    def __prompt_stack_content_message_content(self, content: BaseMessageContent) -> dict:
        if isinstance(content, TextMessageContent):
            return {"text": content.artifact.to_text()}
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __to_role(self, message: Message) -> str:
        if message.is_system():
            return "SYSTEM"
        elif message.is_user():
            return "USER"
        else:
            return "CHATBOT"
