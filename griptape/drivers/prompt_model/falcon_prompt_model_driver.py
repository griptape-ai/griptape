from attr import define
from griptape.artifacts import TextArtifact
from griptape.core import PromptStack
from griptape.drivers import BasePromptModelDriver


@define
class FalconPromptModelDriver(BasePromptModelDriver):
    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str:
        return self.prompt_driver.prompt_stack_to_string(prompt_stack)

    def model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_driver.prompt_stack_to_string(prompt_stack)

        return {
            "max_new_tokens": self.prompt_driver.max_output_tokens(prompt),
            "temperature": self.prompt_driver.temperature,
            "do_sample": True,
            "stop": self.prompt_driver.tokenizer.stop_sequences
        }

    def process_output(self, output: list[dict]) -> TextArtifact:
        return TextArtifact(
            output[0]["generated_text"].strip()
        )
