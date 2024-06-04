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
        if self._tokenizer is None:
            self._tokenizer = HuggingFaceTokenizer(
                tokenizer=import_optional_dependency("transformers").AutoTokenizer.from_pretrained(
                    "meta-llama/Meta-Llama-3-8B-Instruct", model_max_length=self.DEFAULT_MAX_INPUT_TOKENS
                ),
                max_output_tokens=self.max_tokens or self.DEFAULT_MAX_INPUT_TOKENS,
            )
        return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str:
        return self.tokenizer.tokenizer.apply_chat_template(  # pyright: ignore
            [{"role": i.role, "content": i.content} for i in prompt_stack.inputs],
            tokenize=False,
            add_generation_prompt=True,
        )

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_driver.prompt_stack_to_string(prompt_stack)
        return {
            "max_new_tokens": self.prompt_driver.max_output_tokens(prompt),
            "temperature": self.prompt_driver.temperature,
            "stop": self.tokenizer.tokenizer.eos_token,
        }

    def process_output(self, output: dict | list[dict] | str | bytes) -> TextArtifact:
        # This output format is specific to the Llama 3 Instruct models when deployed via SageMaker JumpStart.
        if isinstance(output, dict):
            return TextArtifact(output["generated_text"])
        else:
            raise ValueError("Invalid output format.")
