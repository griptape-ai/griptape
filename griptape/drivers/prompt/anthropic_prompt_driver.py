from typing import Optional
import anthropic
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer


@define
class AnthropicPromptDriver(BasePromptDriver):
    api_key: str = field(kw_only=True, metadata={"env": "ANTHROPIC_API_KEY"})
    max_tokens_to_sample: int = field(default=100, kw_only=True)

    tokenizer: AnthropicTokenizer = field(
        default=Factory(lambda self: AnthropicTokenizer(model=self.model), takes_self=True),
        kw_only=True
    )

    def try_run(self, value: any) -> TextArtifact:
        return self.__run_completion(value)

    def __run_completion(self, value: str) -> TextArtifact:
        client = anthropic.Client(self.api_key)

        response = client.completion(
            prompt=f"{anthropic.HUMAN_PROMPT}{value}{anthropic.AI_PROMPT}",
            stop_sequences = [anthropic.HUMAN_PROMPT],
            model=self.model,
            max_tokens_to_sample=self.max_tokens_to_sample,
        )

        return TextArtifact(
            value=response['completion']
        )
