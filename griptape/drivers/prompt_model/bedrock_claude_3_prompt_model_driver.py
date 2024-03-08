from __future__ import annotations
from typing import Optional, Any
import json
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptModelDriver, AmazonBedrockPromptDriver
from griptape.tokenizers import BedrockClaudeTokenizer


@define
class BedrockClaude3PromptModelDriver(BasePromptModelDriver):
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

    # https://docs.anthropic.com/claude/reference/claude-on-amazon-bedrock
    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> list[Any]:
        system_input = "".join(prompt_input.content for prompt_input in prompt_stack.inputs if prompt_input.is_system())
        inputs = [
            {"role": prompt_input.role, "content": prompt_input.content}
            for prompt_input in prompt_stack.inputs
            if prompt_input.is_user() or prompt_input.is_assistant()
        ]
        return [system_input, inputs]

    # https://docs.anthropic.com/claude/reference/messages_post
    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        system, messages = self.prompt_stack_to_model_input(prompt_stack)

        return {
            "max_tokens": self.tokenizer.max_tokens,
            "system": system,
            "messages": messages,
            "anthropic_version": "bedrock-2023-05-31",
            "stop_sequences": self.tokenizer.stop_sequences,
        }

    def process_output(self, output: list[dict] | str | bytes) -> TextArtifact:
        if isinstance(output, bytes):
            body = json.loads(output.decode())
        else:
            raise Exception("Output must be bytes.")

        return TextArtifact(value=body["content"][0]["text"])
