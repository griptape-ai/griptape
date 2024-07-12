from __future__ import annotations

import uuid
from typing import Optional

from attrs import Factory, define, field

from griptape.mixins import SerializableMixin


@define(kw_only=True)
class Reference(SerializableMixin):
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), metadata={"serializable": True})
    title: str = field(metadata={"serializable": True})
    authors: list[str] = field(factory=list, metadata={"serializable": True})
    source: Optional[str] = field(default=None, metadata={"serializable": True})
    year: Optional[str] = field(default=None, metadata={"serializable": True})
    url: Optional[str] = field(default=None, metadata={"serializable": True})
