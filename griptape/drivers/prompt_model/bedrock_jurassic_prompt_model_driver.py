from __future__ import annotations
from typing import Optional
import json
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import BedrockJurassicTokenizer
from griptape.drivers import AmazonBedrockPromptDriver


@define
class BedrockJurassicPromptModelDriver(BasePromptModelDriver):
    top_p: float = field(default=0.9, kw_only=True, metadata={"serializable": True})
    _tokenizer: BedrockJurassicTokenizer = field(default=None, kw_only=True)
    prompt_driver: Optional[AmazonBedrockPromptDriver] = field(default=None, kw_only=True)
    supports_streaming: bool = field(default=False, kw_only=True)

    @property
    def tokenizer(self) -> BedrockJurassicTokenizer:
        """Returns the tokenizer for this driver.

        We need to pass the `session` field from the Prompt Driver to the
        Tokenizer. However, the Prompt Driver is not initialized until after
        the Prompt Model Driver is initialized. To resolve this, we make the `tokenizer`
        field a @property that is only initialized when it is first accessed.
        This ensures that by the time we need to initialize the Tokenizer, the
        Prompt Driver has already been initialized.

        See this thread more more information: https://github.com/griptape-ai/griptape/issues/244

        Returns:
            BedrockJurassicTokenizer: The tokenizer for this driver.
        """
        if self._tokenizer:
            return self._tokenizer
        else:
            self._tokenizer = BedrockJurassicTokenizer(model=self.prompt_driver.model)
            return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_user():
                prompt_lines.append(f"User: {i.content}")
            elif i.is_assistant():
                prompt_lines.append(f"Assistant: {i.content}")
            elif i.is_system():
                prompt_lines.append(f"System: {i.content}")
            else:
                prompt_lines.append(i.content)
        prompt_lines.append("Assistant:")

        prompt = "\n".join(prompt_lines)

        return {"prompt": prompt}

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_model_input(prompt_stack)["prompt"]

        return {
            "maxTokens": self.prompt_driver.max_output_tokens(prompt),
            "temperature": self.prompt_driver.temperature,
            "stopSequences": self.tokenizer.stop_sequences,
            "countPenalty": {"scale": 0},
            "presencePenalty": {"scale": 0},
            "frequencyPenalty": {"scale": 0},
        }

    def process_output(self, output: list[dict] | str | bytes) -> TextArtifact:
        if isinstance(output, bytes):
            body = json.loads(output.decode())
        else:
            raise Exception("Output must be bytes.")
        return TextArtifact(body["completions"][0]["data"]["text"])
