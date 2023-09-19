import json
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import AnthropicTokenizer


@define
class BedrockClaudePromptModelDriver(BasePromptModelDriver):
    model: str = field(default="anthropic.claude-v2", kw_only=True)
    tokenizer: AnthropicTokenizer = field(
        default=Factory(
            lambda self: AnthropicTokenizer(model=self.model),
            takes_self=True
        ),
        kw_only=True,
    )
    top_p: float = field(default=0.999, kw_only=True)
    top_k: int = field(default=250, kw_only=True)

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_assistant():
                prompt_lines.append(f"Assistant: {i.content}")
            else:
                prompt_lines.append(f"Human: {i.content}")

        prompt_lines.append("Assistant:")

        prompt = "\n".join(prompt_lines)
        return {"prompt": prompt}

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_driver.prompt_stack_to_string(prompt_stack)

        return {
            "max_tokens_to_sample": self.prompt_driver.max_output_tokens(prompt),
            "stop_sequences": self.tokenizer.stop_sequences,
            "temperature": self.prompt_driver.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
        }

    def process_output(self, response_body: bytes) -> TextArtifact:
        body = json.loads(response_body.decode())

        return TextArtifact(body["completion"])
