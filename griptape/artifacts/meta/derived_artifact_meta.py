from attr import Factory, define, field

from griptape.artifacts.list_artifact import ListArtifact
from .base_meta import BaseMeta


@define
class DerivedArtifactMeta(BaseMeta):
    sources: ListArtifact = field(default=Factory(ListArtifact), kw_only=True, metadata={"serializable": True})
