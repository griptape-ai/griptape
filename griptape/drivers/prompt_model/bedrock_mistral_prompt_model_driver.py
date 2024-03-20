from __future__ import annotations
import json
import itertools as it
from typing import Optional
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import BedrockMistralTokenizer
from griptape.drivers import AmazonBedrockPromptDriver
from griptape.utils import J2


@define
class BedrockMistralPromptModelDriver(BasePromptModelDriver):
    BOS_TOKEN = "<s>"
    EOS_TOKEN = "</s>"

    top_p: Optional[float] = field(default=None, kw_only=True)
    top_k: Optional[float] = field(default=None, kw_only=True)
    _tokenizer: BedrockMistralTokenizer = field(default=None, kw_only=True)
    prompt_driver: Optional[AmazonBedrockPromptDriver] = field(default=None, kw_only=True)

    @property
    def tokenizer(self) -> BedrockMistralTokenizer:
        """Returns the tokenizer for this driver.

        We need to pass the `session` field from the Prompt Driver to the
        Tokenizer. However, the Prompt Driver is not initialized until after
        the Prompt Model Driver is initialized. To resolve this, we make the `tokenizer`
        field a @property that is only initialized when it is first accessed.
        This ensures that by the time we need to initialize the Tokenizer, the
        Prompt Driver has already been initialized.

        See this thread more more information: https://github.com/griptape-ai/griptape/issues/244

        Returns:
            BedrockLlamaTokenizer: The tokenizer for this driver.
        """
        if self._tokenizer:
            return self._tokenizer
        else:
            self._tokenizer = BedrockMistralTokenizer(model=self.prompt_driver.model)
            return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str:
        """
        Converts a `PromptStack` to a string that can be used as the input to the model.

        Prompt structure adapted from https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1#instruction-format

        Args:
            prompt_stack: The `PromptStack` to convert.
        """
        system_input = next((i for i in prompt_stack.inputs if i.is_system()), None)
        non_system_inputs = [i for i in prompt_stack.inputs if not i.is_system()]
        if system_input is not None:
            non_system_inputs[0].content = f"{system_input.content} {non_system_inputs[0].content}"

        prompt_lines = [self.BOS_TOKEN]
        for prompt_input in non_system_inputs:
            if prompt_input.is_assistant():
                prompt_lines.append(f"{prompt_input.content}{self.EOS_TOKEN} ")
            else:
                prompt_lines.append(f"[INST] {prompt_input.content} [/INST]")

        return "".join(prompt_lines)

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_model_input(prompt_stack)

        return {
            "prompt": prompt,
            "stop": self.tokenizer.stop_sequences,
            "temperature": self.prompt_driver.temperature,
            "max_tokens": self.prompt_driver.max_output_tokens(prompt),
            **({"top_p": self.top_p} if self.top_p else {}),
            **({"top_k": self.top_k} if self.top_k else {}),
        }

    def process_output(self, output: list[dict] | str | bytes) -> TextArtifact:
        # When streaming, the response body comes back as bytes.
        if isinstance(output, bytes):
            output = output.decode()
        elif isinstance(output, list):
            raise Exception("Invalid output format.")

        body = json.loads(output)
        outputs = body["outputs"]

        if len(outputs) == 1:
            return TextArtifact(outputs[0]["text"])
        else:
            raise Exception("Completion with more than one choice is not supported yet.")
