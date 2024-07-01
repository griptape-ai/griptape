from __future__ import annotations

from abc import ABC

from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin


@define
class BaseDeltaMessageContent(ABC, SerializableMixin):
    index: int = field(kw_only=True, default=0, metadata={"serializable": True})
