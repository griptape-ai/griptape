import uuid

from attrs import Factory, define, field

from griptape.artifacts.base_artifact import BaseArtifact
from griptape.mixins import SerializableMixin


@define
class Run(SerializableMixin):
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True, metadata={"serializable": True})
    input: BaseArtifact = field(kw_only=True, metadata={"serializable": True})
    output: BaseArtifact = field(kw_only=True, metadata={"serializable": True})
