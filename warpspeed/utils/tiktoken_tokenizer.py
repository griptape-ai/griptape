from typing import Optional

from attrs import define, field
import tiktoken

from warpspeed.utils import Tokenizer


@define(frozen=True)
class TiktokenTokenizer(Tokenizer):
    DEFAULT_MODEL = "text-davinci-003"

    MODEL_TO_ENCODING = {
        "gpt-3.5-turbo": "p50k_base",
        "test": "test"
    }

    MODEL_TO_MAX_TOKENS = {
        "gpt-3.5-turbo": 4000,
        "text-davinci-003": 4000,
        "text-curie-001": 2048,
        "text-babbage-001": 2048,
        "text-ada-001": 2048,
        "code-davinci-002": 8000,
        "code-cushman-001": 2048
    }

    model: str = field(default=DEFAULT_MODEL, kw_only=True)
    stop_token: str = field(default=Tokenizer.DEFAULT_STOP_TOKEN, kw_only=True)

    def encode(self, text: str) -> list[int]:
        return self.encoding.encode(text, allowed_special={self.stop_token})

    def decode(self, tokens: list[int]) -> str:
        return self.encoding.decode(tokens)

    def token_count(self, text: str) -> int:
        return len(self.encode(text))

    def tokens_left(self, text: str) -> Optional[int]:
        max_tokens = self.max_tokens

        if max_tokens:
            diff = max_tokens - self.token_count(text)

            if diff > 0:
                return diff
            else:
                return None
        else:
            return None

    @property
    def encoding(self) -> tiktoken.Encoding:
        custom_encoding = self.MODEL_TO_ENCODING.get(self.model)

        if custom_encoding:
            return tiktoken.get_encoding(custom_encoding)
        else:
            return tiktoken.encoding_for_model(self.model)

    @property
    def max_tokens(self) -> Optional[int]:
        return self.MODEL_TO_MAX_TOKENS.get(self.model)
