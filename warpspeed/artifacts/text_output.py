from typing import Optional
from attrs import define, field
from warpspeed.artifacts import StructureArtifact
from warpspeed.utils import TiktokenTokenizer, Tokenizer


@define(frozen=True)
class TextOutput(StructureArtifact):
    meta: Optional[any] = field(default=None)
    tokenizer: Tokenizer = field(default=TiktokenTokenizer(), kw_only=True)

    def token_count(self) -> Optional[int]:
        if isinstance(self.value, str):
            return self.tokenizer.token_count(self.value)
        else:
            return None
