from __future__ import annotations
import json
import itertools as it
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptModelDriver
from griptape.tokenizers import BedrockLlamaTokenizer
from griptape.drivers import AmazonBedrockPromptDriver


@define
class BedrockLlamaPromptModelDriver(BasePromptModelDriver):
    top_p: float = field(default=0.9, kw_only=True)
    _tokenizer: BedrockLlamaTokenizer = field(default=None, kw_only=True)
    prompt_driver: AmazonBedrockPromptDriver | None = field(default=None, kw_only=True)

    @property
    def tokenizer(self) -> BedrockLlamaTokenizer:
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
            self._tokenizer = BedrockLlamaTokenizer(model=self.prompt_driver.model)
            return self._tokenizer

    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str:
        """
        Converts a `PromptStack` to a string that can be used as the input to the model.

        Prompt structure adapted from https://huggingface.co/blog/llama2#how-to-prompt-llama-2

        Args:
            prompt_stack: The `PromptStack` to convert.
        """
        prompt_lines = []

        inputs = iter(prompt_stack.inputs)
        batched_inputs: list[tuple[PromptStack.Input | None, PromptStack.Input | None]] = list(
            it.zip_longest(inputs, inputs)
        )
        for input in batched_inputs:
            first, second = input

            if first.is_system():
                prompt_lines.append(f"<s>[INST] <<SYS>>\n{first.content}\n<</SYS>>\n\n")
                if second:
                    if second.is_user():
                        prompt_lines.append(f"{second.content} [/INST]")
                    else:
                        raise Exception("System input must be followed by user input.")
            elif first.is_assistant():
                prompt_lines.append(f" {first.content} </s>")
                if second:
                    if second.is_user():
                        prompt_lines.append(f"<s>[INST] {second.content} [/INST]")
                    else:
                        raise Exception("Assistant input must be followed by user input.")
            elif first.is_user():
                prompt_lines.append(f"<s>[INST] {first.content} [/INST]")
                if second:
                    if second.is_assistant():
                        prompt_lines.append(f" {second.content} </s>")
                    else:
                        raise Exception("User input must be followed by assistant input.")

        return "".join(prompt_lines)

    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_model_input(prompt_stack)
        print(prompt)

        return {
            "prompt": prompt,
            "max_gen_len": self.prompt_driver.max_output_tokens(prompt),
            "temperature": self.prompt_driver.temperature,
            "top_p": self.top_p,
        }

    def process_output(self, output: list[dict] | str | bytes) -> TextArtifact:
        # When streaming, the response body comes back as bytes.
        if isinstance(output, bytes):
            output = output.decode()
        elif isinstance(output, list):
            raise Exception("Invalid output format.")

        body = json.loads(output)

        return TextArtifact(body["generation"])
