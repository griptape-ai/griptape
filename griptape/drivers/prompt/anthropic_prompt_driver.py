import anthropic
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.core import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer


@define
class AnthropicPromptDriver(BasePromptDriver):
    api_key: str = field(kw_only=True)
    model: str = field(default=AnthropicTokenizer.DEFAULT_MODEL, kw_only=True)
    tokenizer: AnthropicTokenizer = field(
        default=Factory(
            lambda self: AnthropicTokenizer(model=self.model), takes_self=True
        ),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_assistant():
                prompt_lines.append(f"Assistant: {i.content}")
            else:
                prompt_lines.append(f"Human: {i.content}")

        prompt_lines.append("Assistant:")

        prompt = "\n\n" + "\n\n".join(prompt_lines)
        response = anthropic.Anthropic(api_key=self.api_key).completions.create(
            prompt=prompt,
            stop_sequences=self.tokenizer.stop_sequences,
            model=self.model,
            max_tokens_to_sample=self.max_output_tokens(prompt),
            temperature=self.temperature,
        )

        return TextArtifact(value=response.completion)
