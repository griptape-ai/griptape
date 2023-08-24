from attr import define
from griptape.artifacts import TextArtifact
from griptape.core import PromptStack
from griptape.prompt_model_adapters import BasePromptModelAdapter


@define
class LlamaPromptModelAdapter(BasePromptModelAdapter):
    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> list:
        return [
            {"role": i.role, "content": i.content}
            for i in prompt_stack.inputs
        ]

    def model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_driver.prompt_stack_to_string(prompt_stack)

        return {
            "max_new_tokens": self.prompt_driver.max_output_tokens(prompt),
            "temperature": self.prompt_driver.temperature,
        }

    def process_output(self, output: dict) -> TextArtifact:
        return TextArtifact(
            output["generation"]["content"].strip()
        )
