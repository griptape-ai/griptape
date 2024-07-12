from __future__ import annotations

from attrs import define, field

from griptape.common import BaseDeltaMessageContent


@define
class TextDeltaMessageContent(BaseDeltaMessageContent):
    text: str = field(metadata={"serializable": True})
