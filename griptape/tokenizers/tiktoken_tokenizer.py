from attr import define, field
import tiktoken
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class TiktokenTokenizer(BaseTokenizer):
    DEFAULT_OPENAI_GPT_3_MODEL = "gpt-3.5-turbo"
    DEFAULT_OPENAI_GPT_4_MODEL = "gpt-4"
    DEFAULT_AZURE_OPENAI_GPT_3_MODEL = "gpt-35-turbo"
    DEFAULT_AZURE_OPENAI_GPT_4_MODEL = "gpt-4"
    DEFAULT_ENCODING = "cl100k_base"
    DEFAULT_MAX_TOKENS = 2049
    TOKEN_OFFSET = 8

    MODEL_PREFIXES_TO_MAX_TOKENS = {
        "gpt-4-32k": 32768,
        "gpt-4": 8192,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-3.5-turbo": 4096,
        "gpt-35-turbo-16k": 16384,  # Azure OpenAI
        "gpt-35-turbo": 4096,  # Azure OpenAI
        "text-davinci-003": 4097,
        "text-davinci-002": 4097,
        "code-davinci-002": 8001,
        "text-embedding-ada-002": 8191,
        "text-embedding-ada-001": 2046
    }

    EMBEDDING_MODELS = [
        "text-embedding-ada-002",
        "text-embedding-ada-001"
    ]

    CHAT_API_PREFIXES = [
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-35-turbo"  # Azure OpenAI
    ]

    model: str = field(default=DEFAULT_OPENAI_GPT_3_MODEL, kw_only=True)

    @property
    def encoding(self) -> tiktoken.Encoding:
        try:
            return tiktoken.encoding_for_model(self.model)
        except KeyError:
            return tiktoken.get_encoding(self.DEFAULT_ENCODING)

    @property
    def max_tokens(self) -> int:
        tokens = next(v for k, v in self.MODEL_PREFIXES_TO_MAX_TOKENS.items() if self.model.startswith(k))
        offset = 0 if self.model in self.EMBEDDING_MODELS else self.TOKEN_OFFSET

        return (tokens if tokens else self.DEFAULT_MAX_TOKENS) - offset

    def encode(self, text: str) -> list[int]:
        return self.encoding.encode(text, allowed_special=set(self.stop_sequences))

    def decode(self, tokens: list[int]) -> str:
        return self.encoding.decode(tokens)

    def is_chat(self) -> bool:
        return any(self.model.startswith(p) for p in self.CHAT_API_PREFIXES)
