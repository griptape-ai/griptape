from typing import Optional
import json
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptModelDriver, AmazonBedrockPromptDriver
from griptape.tokenizers import BedrockClaudeTokenizer


@define
class BedrockClaudePromptModelDriver(BasePromptModelDriver):
    top_p: float = field(default=0.999, kw_only=True)
    top_k: int = field(default=250, kw_only=True)
    _tokenizer: BedrockClaudeTokenizer = field(default=None, kw_only=True)
    prompt_driver: Optional[AmazonBedrockPromptDriver] = field(default=None, kw_only=True)

    @property
    def tokenizer(self) -> BedrockClaudeTokenizer:
        """Returns the tokenizer for this driver.

        We need to pass the `session` field from the Prompt Driver to the
        Tokenizer. However, the Prompt Driver is not initialized until after
        the Prompt Model Driver is initialized. To resolve this, we make the `tokenizer`
        field a @property that is only initialized when it is first accessed.
        This ensures that by the time we need to initialize the Tokenizer, the
        Prompt Driver has already been initialized.

        See this thread more more information: https://github.com/griptape-ai/griptape/issues/244

        Returns:
            BedrockClaudeTokenizer: The tokenizer for this driver.
        """
        if self._tokenizer:
            return self._tokenizer
        else:
            self._tokenizer = BedrockClaudeTokenizer(model=self.prompt_driver.model)
            return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_assistant():
                prompt_lines.append(f"Assistant: {i.content}")
            else:
                prompt_lines.append(f"Human: {i.content}")

        prompt_lines.append("Assistant:")

        return {"prompt": "\n\n" + "\n\n".join(prompt_lines)}

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_model_input(prompt_stack)["prompt"]

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
