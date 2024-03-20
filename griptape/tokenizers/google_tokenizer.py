from __future__ import annotations
from attr import define, field, Factory
from typing import TYPE_CHECKING
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel


@define()
class GoogleTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"gemini": 30720}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"gemini": 2048}

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    model_client: GenerativeModel = field(
        default=Factory(lambda self: self._default_model_client(), takes_self=True), kw_only=True
    )

    def count_tokens(self, text: str | list) -> int:
        if isinstance(text, str) or isinstance(text, list):
            return self.model_client.count_tokens(text).total_tokens
        else:
            raise ValueError("Text must be a string or a list.")

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)
