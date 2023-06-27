import anthropic
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer


@define
class AnthropicPromptDriver(BasePromptDriver):
    prompt_prefix: str = field(default=anthropic.HUMAN_PROMPT, kw_only=True)
    prompt_suffix: str = field(default=anthropic.AI_PROMPT, kw_only=True)
    api_key: str = field(kw_only=True)
    model: str = field(default=AnthropicTokenizer.DEFAULT_MODEL, kw_only=True)
    tokenizer: AnthropicTokenizer = field(
        default=Factory(
            lambda self: AnthropicTokenizer(model=self.model), takes_self=True
        ),
        kw_only=True,
    )

    def try_run(self, value: str) -> TextArtifact:
        return self.__run_completion(value)

    def __run_completion(self, value: str) -> TextArtifact:
        client = anthropic.Client(self.api_key)

        # Anthropic requires specific prompt formatting: https://console.anthropic.com/docs/api
        response = client.completion(
            prompt=value,
            stop_sequences=self.tokenizer.stop_sequences,
            model=self.model,
            max_tokens_to_sample=self.tokenizer.tokens_left(value),
            temperature=self.temperature,
        )

        return TextArtifact(value=response["completion"])
