from __future__ import annotations
from typing import TYPE_CHECKING, Iterator
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import CohereTokenizer
from griptape.utils import PromptStack, import_optional_dependency
from griptape.processors import AmazonComprehendPiiProcessor

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
        pii_processor: Custom `AmazonComprehendPiiProcessor`.
    """

    api_key: str = field(kw_only=True)
    model: str = field(kw_only=True)
    pii_processor: AmazonComprehendPiiProcessor = field(default=AmazonComprehendPiiProcessor(), kw_only=True)
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True),
        kw_only=True,
    )
    tokenizer: CohereTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        prompt_stack = self.pii_processor.before_run(prompt_stack)
        result = self.client.generate(**self._base_params(prompt_stack))

        if result.generations:
            if len(result.generations) == 1:
                generation = result.generations[0]
                result = TextArtifact(value=generation.text.strip())
                result = self.pii_processor.after_run(result)
                return result
            else:
                raise Exception("completion with more than one choice is not supported yet")
        else:
            raise Exception("model response is empty")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        prompt_stack = self.pii_processor.before_run(prompt_stack)
        result = self.client.generate(**self._base_params(prompt_stack), stream=True)

        for chunk in result:
            chunk = TextArtifact(value=chunk.text)
            chunk = self.pii_processor.after_run(chunk)
            yield chunk

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_string(prompt_stack)
        return {
            "prompt": self.prompt_stack_to_string(prompt_stack),
            "model": self.model,
            "temperature": self.temperature,
            "end_sequences": self.tokenizer.stop_sequences,
            "max_tokens": self.max_output_tokens(prompt),
        }
