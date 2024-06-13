from __future__ import annotations

from abc import ABC
from typing import Optional

from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin


@define
class BaseDeltaPromptStackContent(ABC, SerializableMixin):
    index: int = field(kw_only=True, default=0, metadata={"serializable": True})
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
