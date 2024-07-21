from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.tokenizers import BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from anthropic import Anthropic


@define()
class AnthropicTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"claude-3": 200000, "claude-2.1": 200000, "claude": 100000}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"claude": 4096}

    client: Anthropic = field(
        default=Factory(lambda: import_optional_dependency("anthropic").Anthropic()),
        kw_only=True,
    )

    def count_tokens(self, text: str) -> int:
        return self.client.count_tokens(text)
