import json
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import BedrockJurassicTokenizer
from griptape.drivers import AmazonBedrockPromptDriver


@define
class BedrockJurassicPromptModelDriver(BasePromptModelDriver):
    model: str = field(default="ai21.j2-ultra", kw_only=True)
    top_p: float = field(default=0.9, kw_only=True)
    _tokenizer: BedrockJurassicTokenizer = field(default=None, kw_only=True)

    @property
    def tokenizer(self) -> BedrockJurassicTokenizer:
        if self._tokenizer:
            return self._tokenizer
        else:
            if isinstance(self.prompt_driver, AmazonBedrockPromptDriver):
                self._tokenizer = BedrockJurassicTokenizer(model=self.model, session=self.prompt_driver.session)
                return self._tokenizer
            else:
                raise ValueError("prompt_driver must be of instance AmazonBedrockPromptDriver")

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_user():
                prompt_lines.append(f"\n\nUser: {i.content}")
            elif i.is_assistant():
                prompt_lines.append(f"\n\nBot: {i.content}")
            elif i.is_system():
                prompt_lines.append(f"\nInstructions: {i.content}")

        prompt_lines.append("\n\nBot:")
        prompt = "".join(prompt_lines)

        return { "prompt": prompt }

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_driver.prompt_stack_to_string(prompt_stack)

        return {
            "maxTokens": self.prompt_driver.max_output_tokens(prompt),
            "temperature": self.prompt_driver.temperature,
            "stopSequences": self.tokenizer.stop_sequences,
            "countPenalty": {"scale": 0},
            "presencePenalty": {"scale": 0},
            "frequencyPenalty": {"scale": 0},
        }

    def process_output(self, response_body: str) -> TextArtifact:
        body = json.loads(response_body)

        return TextArtifact(body["completions"][0]["data"]["text"])
