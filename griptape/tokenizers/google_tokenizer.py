from __future__ import annotations
from attrs import define, field, Factory
from typing import TYPE_CHECKING
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer
from griptape.common import PromptStack

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel
    from google.generativeai.types import ContentDict


@define()
class GoogleTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"gemini": 30720}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"gemini": 2048}

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    model_client: GenerativeModel = field(
        default=Factory(lambda self: self._default_model_client(), takes_self=True), kw_only=True
    )

    def count_tokens(self, text: str | PromptStack) -> int:
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict

        if isinstance(text, PromptStack):
            messages = [ContentDict(self.prompt_stack_input_to_message(input)) for input in text.inputs]

            return self.try_count_tokens(messages)
        else:
            return self.try_count_tokens(
                ContentDict(self.prompt_stack_input_to_message(PromptStack.Input(content=text, role="user")))
            )

    def try_count_tokens(self, text: ContentDict | list[ContentDict]) -> int:
        print(text)
        return self.model_client.count_tokens(text).total_tokens

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)

    def prompt_stack_input_to_message(self, prompt_input: PromptStack.Input) -> dict:
        parts = [prompt_input.content]

        if prompt_input.is_assistant():
            return {"role": "model", "parts": parts}
        else:
            return {"role": "user", "parts": parts}
