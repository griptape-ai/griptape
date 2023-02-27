from typing import Optional

from attrs import define, field
import tiktoken

from galaxybrain.utils import Tokenizer


@define(frozen=True)
class TiktokenTokenizer(Tokenizer):
    DEFAULT_MODEL = "text-davinci-003"

    model: str = field(default=DEFAULT_MODEL)
    stop_token: str = field(default=Tokenizer.DEFAULT_STOP_TOKEN)

    def encode(self, text: str) -> list[int]:
        return self.encoding().encode(text, allowed_special={self.stop_token})

    def decode(self, tokens: list[int]) -> str:
        return self.encoding().decode(tokens)

    def token_count(self, text: str) -> int:
        return len(self.encode(text))

    def tokens_left(self, text: str) -> Optional[int]:
        max_tokens = self.max_tokens()

        if max_tokens:
            diff = max_tokens - self.token_count(text)

            if diff > 0:
                return diff
            else:
                return None
        else:
            return None

    def encoding(self):
        return tiktoken.encoding_for_model(self.model)

    def max_tokens(self) -> Optional[int]:
        if self.model == "text-davinci-003":
            return 4000
        elif self.model == "text-curie-001":
            return 2048
        elif self.model == "text-babbage-001":
            return 2048
        elif self.model == "text-ada-001":
            return 2048
        elif self.model == "code-davinci-002":
            return 8000
        elif self.model == "code-cushman-001":
            return 2048
        else:
            return None
