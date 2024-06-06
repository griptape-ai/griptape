from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import CohereTokenizer
from griptape.utils import PromptStack, import_optional_dependency

if TYPE_CHECKING:
    from cohere import Client


@define
class CoherePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Cohere API key.
        model: 	Cohere model name.
        client: Custom `cohere.Client`.
        tokenizer: Custom `CohereTokenizer`.
    """

    api_key: str = field(kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True),
        kw_only=True,
    )
    tokenizer: CohereTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        result = self.client.chat(**self._base_params(prompt_stack))

        return TextArtifact(value=result.text)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        result = self.client.chat_stream(**self._base_params(prompt_stack))

        for event in result:
            if event.event_type == "text-generation":
                yield TextArtifact(value=event.text)

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        user_message = prompt_stack.inputs[-1].content
        history_messages = [self.__to_cohere_message(input) for input in prompt_stack.inputs[:-1]]

        return {
            "message": user_message,
            "chat_history": history_messages,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
        }

    def __to_cohere_message(self, input: PromptStack.Input) -> dict[str, Any]:
        return {"role": self.__to_cohere_role(input.role), "text": input.content}

    def __to_cohere_role(self, role: str) -> str:
        if role == PromptStack.SYSTEM_ROLE:
            return "SYSTEM"
        if role == PromptStack.USER_ROLE:
            return "USER"
        elif role == PromptStack.ASSISTANT_ROLE:
            return "CHATBOT"
        else:
            return "USER"
