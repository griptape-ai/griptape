from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import CohereTokenizer
from griptape.common import (
    PromptStack,
    PromptStackElement,
    DeltaPromptStackElement,
    BaseDeltaPromptStackContent,
    TextPromptStackContent,
    BasePromptStackContent,
)
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from cohere import Client


@define
class CoherePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Cohere API key.
        model: 	Cohere model name.
        client: Custom `cohere.Client`.
    """

    api_key: str = field(kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True),
        kw_only=True,
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        result = self.client.chat(**self._base_params(prompt_stack))

        return TextArtifact(value=result.text)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        result = self.client.chat_stream(**self._base_params(prompt_stack))

        for event in result:
            if event.event_type == "text-generation":
                yield TextArtifact(value=event.text)

    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        if len(prompt_input.content) == 1:
            message_content = self.prompt_stack_content_to_message_content(prompt_input.content[0])

            if prompt_input.is_system():
                return {"role": "SYSTEM", "message": message_content}
            elif prompt_input.is_user():
                return {"role": "USER", "message": message_content}
            else:
                return {"role": "CHATBOT", "message": message_content}
        else:
            raise ValueError("Cohere does not support multiple prompt stack contents.")

    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> str:
        if isinstance(content, TextPromptStackContent):
            return content.artifact.to_text()
        else:
            raise ValueError("Cohere does not support non-text prompt stack contents.")

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        user_message = prompt_stack.inputs[-1].content

        history_messages = [
            self.prompt_stack_input_to_message(input) for input in prompt_stack.inputs[:-1] if not input.is_system()
        ]

        system = next((self.prompt_stack_input_to_message(i) for i in prompt_stack.inputs if i.is_system()), None)

        return {
            "message": user_message,
            "chat_history": history_messages,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "max_tokens": self.max_tokens,
            **({"preamble": system} if system else {}),
        }
