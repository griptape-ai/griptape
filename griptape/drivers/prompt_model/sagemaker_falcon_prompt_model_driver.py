from __future__ import annotations

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import HuggingFaceTokenizer
from griptape.tokenizers.base_tokenizer import BaseTokenizer
from griptape.utils import PromptStack, import_optional_dependency


@define
class SageMakerFalconPromptModelDriver(BasePromptModelDriver):
    DEFAULT_MAX_INPUT_TOKENS = 600

    _tokenizer: HuggingFaceTokenizer = field(default=None, kw_only=True)

    @property
    def tokenizer(self) -> BaseTokenizer:
        if self._tokenizer is None and self.prompt_driver is not None:
            self._tokenizer = HuggingFaceTokenizer(
                tokenizer=import_optional_dependency("transformers").AutoTokenizer.from_pretrained("tiiuae/falcon-40b"),
                max_output_tokens=self.prompt_driver.max_tokens or self.DEFAULT_MAX_INPUT_TOKENS,
            )
        return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str:
        return self.tokenizer.prompt_stack_to_string(prompt_stack)

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        return {
            "max_new_tokens": self.prompt_driver.max_tokens,
            "temperature": self.prompt_driver.temperature,
            "do_sample": True,
            "stop": [
                *(self.tokenizer.tokenizer.eos_token if isinstance(self.tokenizer, HuggingFaceTokenizer) else []),
                *self.prompt_driver.tokenizer.stop_sequences,
            ],
        }

    def process_output(self, output: dict | list[dict] | str | bytes) -> TextArtifact:
        if isinstance(output, list):
            return TextArtifact(output[0]["generated_text"].strip())
        else:
            raise ValueError("Invalid output format.")
