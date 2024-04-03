from attr import define, field
from .base_meta import BaseMeta


@define
class WebArtifactMeta(BaseMeta):
    url: str = field(kw_only=True, metadata={"serializable": True})
