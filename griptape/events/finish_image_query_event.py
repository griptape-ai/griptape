from attrs import define, field

from griptape.events.base_image_query_event import BaseImageQueryEvent


@define
class FinishImageQueryEvent(BaseImageQueryEvent):
    result: str = field(kw_only=True, metadata={"serializable": True})
