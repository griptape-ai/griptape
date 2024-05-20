from attr import field
from attrs import define

from griptape.events import BaseChunkEvent


@define
class CompletionChunkEvent(BaseChunkEvent):
    token: str = field(kw_only=True, metadata={"serializable": True})
