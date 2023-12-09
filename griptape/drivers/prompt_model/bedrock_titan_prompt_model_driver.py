from __future__ import annotations
from typing import Optional
import json
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import BedrockTitanTokenizer
from griptape.drivers import AmazonBedrockPromptDriver


@define
class BedrockTitanPromptModelDriver(BasePromptModelDriver):
    top_p: float = field(default=0.9, kw_only=True)
    _tokenizer: BedrockTitanTokenizer = field(default=None, kw_only=True)
    prompt_driver: AmazonBedrockPromptDriver | None = field(default=None, kw_only=True)

    @property
    def tokenizer(self) -> BedrockTitanTokenizer:
        """Returns the tokenizer for this driver.

        We need to pass the `session` field from the Prompt Driver to the
        Tokenizer. However, the Prompt Driver is not initialized until after
        the Prompt Model Driver is initialized. To resolve this, we make the `tokenizer`
        field a @property that is only initialized when it is first accessed.
        This ensures that by the time we need to initialize the Tokenizer, the
        Prompt Driver has already been initialized.

        See this thread more more information: https://github.com/griptape-ai/griptape/issues/244

        Returns:
            BedrockTitanTokenizer: The tokenizer for this driver.
        """
        if self._tokenizer:
            return self._tokenizer
        else:
            self._tokenizer = BedrockTitanTokenizer(model=self.prompt_driver.model)
            return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_user():
                prompt_lines.append(f"User: {i.content}")
            elif i.is_assistant():
                prompt_lines.append(f"Bot: {i.content}")
            elif i.is_system():
                prompt_lines.append(f"Instructions: {i.content}")
            else:
                prompt_lines.append(i.content)
        prompt_lines.append("Bot:")

        prompt = "\n\n".join(prompt_lines)

        return {"inputText": prompt}

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_model_input(prompt_stack)["inputText"]

        return {
            "textGenerationConfig": {
                "maxTokenCount": self.prompt_driver.max_output_tokens(prompt),
                "stopSequences": self.tokenizer.stop_sequences,
                "temperature": self.prompt_driver.temperature,
                "topP": self.top_p,
            }
        }

    def process_output(self, response_body: str | bytes) -> TextArtifact:
        # When streaming, the response body comes back as bytes.
        if isinstance(response_body, bytes):
            response_body = response_body.decode()

        body = json.loads(response_body)

        if self.prompt_driver.stream:
            return TextArtifact(body["outputText"])
        else:
            return TextArtifact(body["results"][0]["outputText"])
