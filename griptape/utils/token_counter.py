from attrs import define, field


@define
class TokenCounter:
    tokens: int = field(default=0, kw_only=True)

    def add_tokens(self, new_tokens: int) -> int:
        self.tokens += new_tokens

        return self.tokens
