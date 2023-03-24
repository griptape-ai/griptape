from attrs import define, field
import tiktoken
from warpspeed.utils import Tokenizer


@define(frozen=True)
class TiktokenTokenizer(Tokenizer):
    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_ENCODING = "cl100k_base"
    DEFAULT_MAX_TOKENS = 2049
    TOKEN_OFFSET = 8

    MODEL_PREFIXES_TO_MAX_TOKENS = {
        "gpt-4-32k": 32768,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 4096,
        "text-davinci-003": 4097,
        "text-davinci-002": 4097,
        "code-davinci-002": 8001
    }

    CHAT_API_PREFIXES = [
        "gpt-3.5-turbo",
        "gpt-4"
    ]

    model: str = field(default=DEFAULT_MODEL, kw_only=True)
    stop_sequence: str = field(default=Tokenizer.DEFAULT_STOP_SEQUENCE, kw_only=True)

    def encode(self, text: str) -> list[int]:
        return self.encoding.encode(text, allowed_special={self.stop_sequence})

    def decode(self, tokens: list[int]) -> str:
        return self.encoding.decode(tokens)

    def token_count(self, text: str) -> int:
        return len(self.encode(text))

    def tokens_left(self, text: str) -> int:
        diff = self.max_tokens - self.token_count(text)

        if diff > 0:
            return diff
        else:
            return 0

    def is_chat(self) -> bool:
        return next(p for p in self.CHAT_API_PREFIXES if self.model.startswith(p)) is not None

    @property
    def encoding(self) -> tiktoken.Encoding:
        try:
            return tiktoken.encoding_for_model(self.model)
        except KeyError:
            return tiktoken.get_encoding(self.DEFAULT_ENCODING)

    @property
    def max_tokens(self) -> int:
        tokens = next(v for k, v in self.MODEL_PREFIXES_TO_MAX_TOKENS.items() if self.model.startswith(k))

        return (tokens if tokens else self.DEFAULT_MAX_TOKENS) - self.TOKEN_OFFSET
