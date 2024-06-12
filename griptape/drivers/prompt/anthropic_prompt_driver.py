from __future__ import annotations
from typing import Optional, Any
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack, import_optional_dependency
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer, BaseTokenizer


@define
class AnthropicPromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
    """

    api_key: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Any = field(
        default=Factory(
            lambda self: import_optional_dependency("anthropic").Anthropic(api_key=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: AnthropicTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    top_p: float = field(default=0.999, kw_only=True, metadata={"serializable": True})
    top_k: int = field(default=250, kw_only=True, metadata={"serializable": True})
    max_tokens: int = field(default=1000, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        response = self.client.messages.create(**self._base_params(prompt_stack))

        return TextArtifact(value=response.content[0].text)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        response = self.client.messages.create(**self._base_params(prompt_stack), stream=True)

        for chunk in response:
            if chunk.type == "content_block_delta":
                yield TextArtifact(value=chunk.delta.text)

    def _prompt_stack_input_to_message(self, prompt_input: PromptStack.Input) -> dict:
        content = prompt_input.content

        if prompt_input.is_system():
            return {"role": "system", "content": content}
        elif prompt_input.is_assistant():
            return {"role": "assistant", "content": content}
        else:
            return {"role": "user", "content": content}

    def _prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict:
        messages = [
            self._prompt_stack_input_to_message(prompt_input)
            for prompt_input in prompt_stack.inputs
            if not prompt_input.is_system()
        ]
        system = next((self._prompt_stack_input_to_message(i) for i in prompt_stack.inputs if i.is_system()), None)

        if system is None:
            return {"messages": messages}
        else:
            return {"messages": messages, "system": system["content"]}

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.max_tokens,
            **self._prompt_stack_to_model_input(prompt_stack),
        }
