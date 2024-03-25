from __future__ import annotations
from typing import Optional, Any
from collections.abc import Iterator
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack, import_optional_dependency
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer


@define
class AnthropicPromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
        tokenizer: Custom `AnthropicTokenizer`.
    """

    api_key: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Any = field(
        default=Factory(
            lambda self: import_optional_dependency("anthropic").Anthropic(api_key=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    tokenizer: AnthropicTokenizer = field(
        default=Factory(lambda self: AnthropicTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    top_p: float = field(default=0.999, kw_only=True, metadata={"serializable": True})
    top_k: int = field(default=250, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        response = self.client.messages.create(**self._base_params(prompt_stack))

        return TextArtifact(value=response.content[0].text)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        response = self.client.messages.create(**self._base_params(prompt_stack), stream=True)

        for chunk in response:
            if chunk.type == "content_block_delta":
                yield TextArtifact(value=chunk.delta.text)

    def _prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict:
        messages = [
            {"role": self.__to_anthropic_role(prompt_input), "content": prompt_input.content}
            for prompt_input in prompt_stack.inputs
            if not prompt_input.is_system()
        ]
        system = next((i for i in prompt_stack.inputs if i.is_system()), None)

        if system is None:
            return {"messages": messages}
        else:
            return {"messages": messages, "system": system.content}

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "max_tokens": self.max_output_tokens(self.prompt_stack_to_string(prompt_stack)),
            "top_p": self.top_p,
            "top_k": self.top_k,
            **self._prompt_stack_to_model_input(prompt_stack),
        }

    def __to_anthropic_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"
