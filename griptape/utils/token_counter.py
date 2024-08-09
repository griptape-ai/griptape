from __future__ import annotations

from attrs import define, field


@define
class TokenCounter:
    tokens: int = field(default=0, kw_only=True)

    def add_tokens(self, new_tokens: int | float) -> int:
        self.tokens += int(new_tokens)

        return self.tokens
