from typing import Iterator
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
        tokenizer: Custom `AnthropicTokenizer`.
    """

    api_key: str = field(kw_only=True)
    model: str = field(kw_only=True)
    tokenizer: AnthropicTokenizer = field(
        default=Factory(lambda self: AnthropicTokenizer(model=self.model), takes_self=True), kw_only=True
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        anthropic = import_optional_dependency("anthropic")

        response = anthropic.Anthropic(api_key=self.api_key).completions.create(**self._base_params(prompt_stack))
        return TextArtifact(value=response.completion)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        anthropic = import_optional_dependency("anthropic")

        response = anthropic.Anthropic(api_key=self.api_key).completions.create(
            **self._base_params(prompt_stack), stream=True
        )

        for chunk in response:
            yield TextArtifact(value=chunk.completion)

    def default_prompt_stack_to_string_converter(self, prompt_stack: PromptStack) -> str:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_assistant():
                prompt_lines.append(f"Assistant: {i.content}")
            else:
                prompt_lines.append(f"Human: {i.content}")

        prompt_lines.append("Assistant:")

        return "\n\n" + "\n\n".join(prompt_lines)

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_string(prompt_stack)

        return {
            "prompt": self.prompt_stack_to_string(prompt_stack),
            "model": self.model,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "max_tokens_to_sample": self.max_output_tokens(prompt),
        }
