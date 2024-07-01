from typing import Optional, Any
from attrs import define, field
from griptape.artifacts import TextArtifact, BaseArtifact


@define(kw_only=True)
class RagContext:
    """Used by RagEngine stages and module to pass context that individual modules are expected to update in the `run`
    method.

    Attributes:
        query: Query provided by the user.
        module_params: Dictionary of dictionary parameters to be used by modules. First key should be the module name and the second a parameter name.
        before_query: An optional list of strings to add before the query in generation modules.
        after_query: An optional list of strings to add after the query in generation modules.
        text_chunks: A list of text chunks to pass around from the retrieval stage to the generation stage.
        output: Final output from the generation stage.
    """

    query: str = field()
    module_params: dict[str, dict] = field(factory=dict)
    before_query: list[str] = field(factory=list)
    after_query: list[str] = field(factory=list)
    text_chunks: list[TextArtifact] = field(factory=list)
    output: Optional[BaseArtifact] = field(default=None)
