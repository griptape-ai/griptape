from __future__ import annotations

from attrs import define, field
from pydantic import BaseModel

from griptape.artifacts.generic_artifact import GenericArtifact


@define
class ModelArtifact(GenericArtifact[BaseModel]):
    """Stores Pydantic models as Artifacts.

    Required since Pydantic models require a custom serialization method.

    Attributes:
        value: The pydantic model to store.
    """

    # We must explicitly define the type rather than rely on the parent T since
    # generic type information is lost at runtime.
    value: BaseModel = field(metadata={"serializable": True})

    def to_text(self) -> str:
        return self.value.model_dump_json()
