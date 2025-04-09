from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.tokenizers import BaseTokenizer
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from google.genai import Client


@define()
class GoogleTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {
        "gemini-2.5-pro-preview": 1048576,
        "gemini-2.0-flash": 1048576,
        "gemini-1.5-pro": 2097152,
        "gemini": 1048576,
    }
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"gemini-2.5-pro-preview": 65536, "gemini": 8192}

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    _client: Optional[Client] = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> Client:
        genai = import_optional_dependency("google.genai")
        return genai.Client(api_key=self.api_key)

    def count_tokens(self, text: str) -> int:
        return self.client.models.count_tokens(model=self.model, contents=text).total_tokens or 0
