from __future__ import annotations
from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer
from vertexai.preview.generative_models import GenerativeModel


@define(frozen=True)
class GeminiTokenizer(BaseTokenizer):
    DEFAULT_GEMINI_TEXT_MODEL = "gemini-pro"
    DEFAULT_GEMINI_VISION_MODEL = "gemini-pro-vision"

    # https://ai.google.dev/models/gemini
    MODEL_PREFIXES_TO_MAX_TOKENS = {"gemini-pro": 30720, "gemini-pro-vision": 12288}
    EMBEDDING_MODELS = ["embedding-001"]

    model: str = field(default=DEFAULT_GEMINI_TEXT_MODEL, kw_only=True)
    gemini: GenerativeModel = field(default=Factory(lambda self: GenerativeModel(self.model), takes_self=True))
    max_tokens: int = field(default=Factory(lambda self: self.default_max_tokens(), takes_self=True), kw_only=True)

    def default_max_tokens(self) -> int:
        tokens = next((v for k, v in self.MODEL_PREFIXES_TO_MAX_TOKENS.items() if self.model == k), None)

        return tokens

    def count_tokens(self, text: str | list) -> int:
        if not isinstance(text, str):
            raise ValueError("Text must be a string.")

        try:
            num_tokens = self.gemini.count_tokens(text)

            return num_tokens.total_tokens
        except Exception as e:
            raise ValueError(f"Error counting tokens: {e}")
