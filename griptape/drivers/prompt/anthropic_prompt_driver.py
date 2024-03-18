from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Iterator
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack, import_optional_dependency
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer

if TYPE_CHECKING:
    from anthropic import Anthropic


@define
class AnthropicPromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
        tokenizer: Custom `AnthropicTokenizer`.
    """

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Anthropic = field(
        default=Factory(
            lambda self: import_optional_dependency("anthropic").Anthropic(api_key=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    tokenizer: AnthropicTokenizer = field(
        default=Factory(lambda self: AnthropicTokenizer(model=self.model), takes_self=True), kw_only=True
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        response = self.client.messages.create(**self._base_params(prompt_stack))

        return TextArtifact(value=response.content[0].text)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        response = self.client.messages.create(**self._base_params(prompt_stack), stream=True)

        for chunk in response:
            if chunk.type == "content_block_delta":
                yield TextArtifact(value=chunk.delta.text)

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict[str, Any]]:
        return [
            {"role": self.__to_anthropic_role(i), "content": i.content}
            for i in prompt_stack.inputs
            if i.is_user() or i.is_assistant()
        ]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = {
            "messages": self._prompt_stack_to_messages(prompt_stack),
            "model": self.model,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "max_tokens": self.max_output_tokens(self.prompt_stack_to_string(prompt_stack)),
        }

        system_input = next((i for i in prompt_stack.inputs if i.is_system()), None)
        if system_input is not None:
            params["system"] = system_input.content

        return params

    def __to_anthropic_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"
