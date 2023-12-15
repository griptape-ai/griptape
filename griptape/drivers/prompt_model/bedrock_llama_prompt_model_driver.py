from __future__ import annotations
import json
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
        prompt_lines = []
        first_user_input = True

        for i in prompt_stack.inputs:
            if i.is_user():
                if first_user_input:
                    prompt_lines.append(f"{i.content} [/INST]")
                    first_user_input = False
                else:
                    prompt_lines.append(f"<s>[INST] {i.content} [/INST]")
            elif i.is_assistant():
                prompt_lines.append(f"{i.content} </s>")
            elif i.is_system():
                prompt_lines.append(f"<s>[INST] <<SYS>>\n{i.content}\n<</SYS>>\n\n")

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

    def process_output(self, response_body: str | bytes) -> TextArtifact:
        # When streaming, the response body comes back as bytes.
        if isinstance(response_body, bytes):
            response_body = response_body.decode()

        body = json.loads(response_body)

        return TextArtifact(body["generation"])
