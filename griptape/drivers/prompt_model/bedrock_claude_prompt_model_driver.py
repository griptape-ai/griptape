from __future__ import annotations
from typing import Optional
import json
from attrs import define, field
from griptape.artifacts import TextArtifact
from griptape.common import PromptStack
from griptape.drivers import BasePromptModelDriver, AmazonBedrockPromptDriver
from griptape.tokenizers import BedrockClaudeTokenizer


@define
class BedrockClaudePromptModelDriver(BasePromptModelDriver):
    ANTHROPIC_VERSION = "bedrock-2023-05-31"  # static string for AWS: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html#api-inference-examples-claude-multimodal-code-example

    top_p: float = field(default=0.999, kw_only=True, metadata={"serializable": True})
    top_k: int = field(default=250, kw_only=True, metadata={"serializable": True})
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
        messages = [
            {"role": self.__to_anthropic_role(prompt_input), "content": prompt_input.content}
            for prompt_input in prompt_stack.inputs
            if not prompt_input.is_system()
        ]
        system = next((i for i in prompt_stack.inputs if i.is_system()), None)

        if system is None:
            return {"messages": messages}
        else:
            return {"messages": messages, "system": system.content}

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        input = self.prompt_stack_to_model_input(prompt_stack)

        return {
            "stop_sequences": self.tokenizer.stop_sequences,
            "temperature": self.prompt_driver.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.prompt_driver.max_output_tokens(self.prompt_driver.prompt_stack_to_string(prompt_stack)),
            "anthropic_version": self.ANTHROPIC_VERSION,
            **input,
        }

    def process_output(self, output: list[dict] | str | bytes) -> TextArtifact:
        if isinstance(output, bytes):
            body = json.loads(output.decode())
        else:
            raise Exception("Output must be bytes.")

        if body["type"] == "content_block_delta":
            return TextArtifact(value=body["delta"]["text"])
        elif body["type"] == "message":
            return TextArtifact(value=body["content"][0]["text"])
        else:
            return TextArtifact(value="")

    def __to_anthropic_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"
