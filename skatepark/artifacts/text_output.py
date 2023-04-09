from typing import Optional
from attr import define, field
from skatepark.artifacts import StructureArtifact
from skatepark.utils import TiktokenTokenizer, Tokenizer


@define(frozen=True)
class TextOutput(StructureArtifact):
    meta: Optional[any] = field(default=None)
    tokenizer: Tokenizer = field(default=TiktokenTokenizer(), kw_only=True)

    def token_count(self) -> Optional[int]:
        if isinstance(self.value, str):
            return self.tokenizer.token_count(self.value)
        else:
            return None
