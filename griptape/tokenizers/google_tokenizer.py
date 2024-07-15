from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.tokenizers import BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel


@define()
class GoogleTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"gemini": 30720}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"gemini": 2048}

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    model_client: GenerativeModel = field(
        default=Factory(lambda self: self._default_model_client(), takes_self=True),
        kw_only=True,
    )

    def count_tokens(self, text: str) -> int:
        return self.model_client.count_tokens(text).total_tokens

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)
