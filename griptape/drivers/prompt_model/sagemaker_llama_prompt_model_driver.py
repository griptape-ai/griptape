from attr import define, field, Factory
from transformers import LlamaTokenizerFast
from griptape.artifacts import TextArtifact
from griptape.core import PromptStack
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import BaseTokenizer, HuggingFaceTokenizer


@define
class SagemakerLlamaPromptModelDriver(BasePromptModelDriver):
    tokenizer: BaseTokenizer = field(
        default=Factory(
            lambda: HuggingFaceTokenizer(
                tokenizer=LlamaTokenizerFast.from_pretrained(
                    "hf-internal-testing/llama-tokenizer",
                    model_max_length=4000
                )
            )
        ),
        kw_only=True
    )

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> list:
        return [[
            {"role": i.role, "content": i.content}
            for i in prompt_stack.inputs
        ]]

    def model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_driver.prompt_stack_to_string(prompt_stack)

        return {
            "max_new_tokens": self.prompt_driver.max_output_tokens(prompt),
            "temperature": self.prompt_driver.temperature,
            "eos_token_id": self.prompt_driver.tokenizer.encode(self.prompt_driver.tokenizer.stop_sequences[0])[1]
        }

    def process_output(self, output: list[dict]) -> TextArtifact:
        return TextArtifact(
            output[0]["generation"]["content"].strip()
        )
