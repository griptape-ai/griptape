from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape import utils
from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact, TextArtifact
    from griptape.common import Reference


@define(kw_only=True)
class RagContext(SerializableMixin):
    """Used by RagEngine stages and module to pass context that individual modules are expected to update in the `run` method.

    Attributes:
        query: Query provided by the user.
        module_configs: Dictionary of module configs. First key should be a module name and the second a dictionary of config parameters.
        before_query: An optional list of strings to add before the query in generation modules.
        after_query: An optional list of strings to add after the query in generation modules.
        text_chunks: A list of text chunks to pass around from the retrieval stage to the generation stage.
        output: Final output from the generation stage.
    """

    query: str = field(metadata={"serializable": True})
    module_configs: dict[str, dict] = field(factory=dict, metadata={"serializable": True})
    before_query: list[str] = field(factory=list, metadata={"serializable": True})
    after_query: list[str] = field(factory=list, metadata={"serializable": True})
    text_chunks: list[TextArtifact] = field(factory=list, metadata={"serializable": True})
    output: Optional[BaseArtifact] = field(default=None, metadata={"serializable": True})

    def get_references(self) -> list[Reference]:
        return utils.references_from_artifacts(self.text_chunks)
