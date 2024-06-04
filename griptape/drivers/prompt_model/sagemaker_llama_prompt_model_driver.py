from __future__ import annotations
from attrs import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack, import_optional_dependency
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import HuggingFaceTokenizer


@define
class SageMakerLlamaPromptModelDriver(BasePromptModelDriver):
    # Default context length for all Llama 3 models is 8K as per https://huggingface.co/blog/llama3
    DEFAULT_MAX_INPUT_TOKENS = 8000

    _tokenizer: HuggingFaceTokenizer = field(default=None, kw_only=True)

    @property
    def tokenizer(self) -> HuggingFaceTokenizer:
        if self._tokenizer is None and self.prompt_driver is not None:
            self._tokenizer = HuggingFaceTokenizer(
                tokenizer=import_optional_dependency("transformers").AutoTokenizer.from_pretrained(
                    "meta-llama/Meta-Llama-3-8B-Instruct"
                ),
                max_output_tokens=self.prompt_driver.max_tokens or self.DEFAULT_MAX_INPUT_TOKENS,
            )
        return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str:
        return self.tokenizer.prompt_stack_to_string(prompt_stack)

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        return {
            "max_new_tokens": self.prompt_driver.max_tokens,
            "temperature": self.prompt_driver.temperature,
            "stop": [self.tokenizer.tokenizer.eos_token, *self.prompt_driver.tokenizer.stop_sequences],
        }

    def process_output(self, output: dict | list[dict] | str | bytes) -> TextArtifact:
        # This output format is specific to the Llama 3 Instruct models when deployed via SageMaker JumpStart.
        if isinstance(output, dict):
            return TextArtifact(output["generated_text"])
        else:
            raise ValueError("Invalid output format.")
