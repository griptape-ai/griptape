from __future__ import annotations

from attrs import define, field

from griptape.events.base_image_query_event import BaseImageQueryEvent


@define
class StartImageQueryEvent(BaseImageQueryEvent):
    query: str = field(kw_only=True, metadata={"serializable": True})
    images_info: list[str] = field(kw_only=True, metadata={"serializable": True})
