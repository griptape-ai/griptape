from attr import define, field

from griptape.artifacts import TextArtifact


@define(kw_only=True)
class RagContext:
    query: str = field()
    text_chunks: list[TextArtifact] = field(factory=list)
    output: str = field(default="")
