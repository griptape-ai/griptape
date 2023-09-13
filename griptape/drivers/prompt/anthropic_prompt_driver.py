import anthropic
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer


@define
class AnthropicPromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name. Defaults to `claude-2`.
        tokenizer: Custom `AnthropicTokenizer`.
    """
    api_key: str = field(kw_only=True)
    model: str = field(default=AnthropicTokenizer.DEFAULT_MODEL, kw_only=True)
    tokenizer: AnthropicTokenizer = field(
        default=Factory(
            lambda self: AnthropicTokenizer(model=self.model), takes_self=True
        ),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        prompt = self.prompt_stack_to_string(prompt_stack)
        response = anthropic.Anthropic(api_key=self.api_key).completions.create(
            prompt=prompt,
            stop_sequences=self.tokenizer.stop_sequences,
            model=self.model,
            max_tokens_to_sample=self.max_output_tokens(prompt),
            temperature=self.temperature,
        )

        return TextArtifact(value=response.completion)

    def default_prompt_stack_to_string_converter(self, prompt_stack: PromptStack) -> str:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_assistant():
                prompt_lines.append(f"Assistant: {i.content}")
            else:
                prompt_lines.append(f"Human: {i.content}")

        prompt_lines.append("Assistant:")

        return "\n\n" + "\n\n".join(prompt_lines)
