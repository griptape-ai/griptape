from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define(kw_only=True)
class Run(SerializableMixin):
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), metadata={"serializable": True})
    meta: Optional[dict] = field(default=None, metadata={"serializable": True})
    input: BaseArtifact = field(metadata={"serializable": True})
    output: BaseArtifact = field(metadata={"serializable": True})
