from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from griptape.tokenizers import BaseTokenizer
from griptape.common import BasePromptStackContent, TextPromptStackContent, PromptStackElement

if TYPE_CHECKING:
    from cohere import Client


@define()
class CohereTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"command-r": 128000, "command": 4096, "embed": 512}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"command": 4096, "embed": 512}

    client: Client = field(kw_only=True)

    def try_count_tokens(self, text: str) -> int:
        return len(self.client.tokenize(text=text, model=self.model).tokens)

    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        if len(prompt_input.content) == 1:
            message_content = self.prompt_stack_content_to_message_content(prompt_input.content[0])

            if prompt_input.is_system():
                return {"role": "SYSTEM", "message": message_content}
            elif prompt_input.is_user():
                return {"role": "USER", "message": message_content}
            else:
                return {"role": "CHATBOT", "message": message_content}
        else:
            raise ValueError("Cohere does not support multiple prompt stack contents.")

    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> str:
        if isinstance(content, TextPromptStackContent):
            return content.artifact.to_text()
        else:
            raise ValueError("Cohere does not support non-text prompt stack contents.")
