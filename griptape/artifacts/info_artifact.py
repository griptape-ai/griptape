from attr import define, field
from griptape.artifacts import BaseArtifact
from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class InfoArtifact(BaseArtifact):
    value: str = field()

    def token_count(self, tokenizer: BaseTokenizer) -> int:
        return tokenizer.token_count(self.value)

    def to_text(self) -> str:
        return self.value

    def to_dict(self) -> dict:
        from griptape.schemas import InfoArtifactSchema

        return dict(InfoArtifactSchema().dump(self))
